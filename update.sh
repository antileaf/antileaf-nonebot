ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/plugins"
ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/toolkit"

scp -r plugins ubuntu@tencentyun:~/antileaf-nonebot
scp -r toolkit ubuntu@tencentyun:~/antileaf-nonebot

# scp -r images ubuntu@tencentyun:~/antileaf-nonebot

echo
echo "----- DONE -----"