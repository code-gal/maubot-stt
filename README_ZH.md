[English](README.md) | 中文

# Whisper Plugin for Maubot

Whisper Plugin 是一个用于 Maubot 的插件，支持在 Matrix 客户端用 OpenAI 的 Whisper API 将音频消息转录为文本。

## 功能

- 自动响应房间中的音频和文件消息
- 调用 OpenAI Whisper API 进行音频转录
- 支持用户和房间白名单
- 支持在线程中回复

![alt text](sample1.png)

## 安装

1. **克隆或下载插件代码**：

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    zip -9r maubot-stt.mbp *
    ```

2. **配置 Maubot**：

    请确保你已经安装并设置好了 Maubot。具体步骤可以参考 [Maubot 的官方文档](https://docs.mau.fi/maubot/usage/basic.html)。

3. **上传插件**：

    在 Maubot 管理界面上传插件。

## 配置

上传插件后，你需要进行一些配置。以下是配置项的说明：

- `api_endpoint`：OpenAI Whisper API 端点，默认为 `https://api.openai.com/v1/audio/transcriptions`。
- `openai_api_key`：你的 OpenAI API 密钥。
- `allowed_users`：允许使用此插件的用户列表。如果为空列表，则允许所有用户使用。
- `allowed_rooms`：允许使用此插件的房间列表。如果为空列表，则允许所有房间使用。

### 配置示例

在 Maubot 管理界面，进入插件的配置页面，填写以下内容：

```json
{
  "api_endpoint": "https://api.openai.com/v1/audio/transcriptions",
  "openai_api_key": "your_openai_api_key",
  "allowed_users": ["@user1:matrix.org", "@user2:matrix.org"],
  "allowed_rooms": ["!roomid:matrix.org"]
}
```

建议关闭实例配置保存后再打开。

## 使用

插件会自动监听房间中的消息，当在接收到语音消息或音频文件时进行以下操作：

1. 下载音频文件。
2. 调用 OpenAI Whisper API 进行转录。
3. 将转录结果以文本消息的形式发送到相应的房间。


## 许可证

本项目采用 MIT 许可证。