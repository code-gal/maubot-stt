import asyncio
import json
import os
import re
import aiohttp
from datetime import datetime
from typing import Type
from mautrix.client import Client
from maubot.handlers import event
from maubot import Plugin, MessageEvent
from mautrix.errors import MatrixRequestError
from mautrix.types import EventType, MessageType, RelationType, TextMessageEventContent, Format,RelatesTo,InReplyTo
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper

class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("whisper_endpoint")
        helper.copy("openai_api_key")
        helper.copy("allowed_users")
        helper.copy("allowed_rooms")
        helper.copy("prompt")
        helper.copy("language")

class WhisperPlugin(Plugin):

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        self.whisper_endpoint = self.config['whisper_endpoint']
        self.api_key = self.config['openai_api_key']
        self.prompt = self.config['prompt']
        self.language = self.config['language']
        self.allowed_users = self.config['allowed_users']
        self.allowed_rooms = self.config['allowed_rooms']
        self.log.debug("Whisper plugin started")

    async def should_respond(self, event: MessageEvent) -> bool:
        if event.sender == self.client.mxid:
            return False

        if self.allowed_users and event.sender not in self.allowed_users:
            return False

        if self.allowed_rooms and event.room_id not in self.allowed_rooms:
            return False

        return event.content.msgtype == MessageType.AUDIO or event.content.msgtype == MessageType.FILE

    @event.on(EventType.ROOM_MESSAGE)
    async def on_message(self, event: MessageEvent) -> None:
        if not await self.should_respond(event):
            return

        try:
            await event.mark_read()
            await self.client.set_typing(event.room_id, timeout=99999)

            audio_bytes = await self.client.download_media(url=event.content.url)
            transcription = await self.transcribe_audio(audio_bytes)

            await self.client.set_typing(event.room_id, timeout=0)

            content = TextMessageEventContent(
                msgtype=MessageType.TEXT,
                body=transcription,
                format=Format.HTML,
                formatted_body=transcription
            )
            in_reply_to = InReplyTo(event_id=event.event_id)
            if event.content.relates_to and event.content.relates_to.rel_type == RelationType.THREAD:
                await event.respond(content, in_thread=True)
            else:
                content.relates_to = RelatesTo(
                    in_reply_to=in_reply_to
                )
                await event.respond(content)

        except Exception as e:
            self.log.exception(f"Something went wrong: {e}")
            await event.respond(f"Something went wrong: {e}")


    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        data = aiohttp.FormData()
        data.add_field('file', audio_bytes, filename='audio.mp3', content_type='audio/mpeg')
        data.add_field('model', 'whisper-1')
        if self.prompt:
            data.add_field('prompt', f"{self.prompt}")
        if self.language:
            data.add_field('language', f"{self.language}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.whisper_endpoint, headers=headers, data=data) as response:
                    if response.status != 200:
                        self.log.error(f"Error response from API: {await response.text()}")
                        return f"Error: {await response.text()}"
                    response_json = await response.json()
                    return response_json.get("text", "Sorry, I can't transcribe the audio.")
        except Exception as e:
            self.log.exception(f"Failed to transcribe audio, msg: {e}")
            return "Sorry, an error occurred while transcribing the audio."

    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    def save_config(self) -> None:
        self.config.save()

    async def update_config(self, new_config: dict) -> None:
        self.config.update(new_config)
        self.save_config()
        self.log.debug("Configuration updated and saved")
