docker run \
  -e TF_SOURCE_CHAT_ID=-100123 \
  -e TF_DESTINATION_CHAT_IDS=-100111,-100222 \
  -e TF_DISABLE_KEYWORDS=true \
  telegramforwarder
