sleep 30s
nohup /usr/bin/python3 /kakaobot/DB_to_Bot.py > /kakaobot/log/DB_to_Bot_Log_$(date '+%Y-%m-%d_%H:%M:%S').txt 2>&1 &

