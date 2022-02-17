ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/plugins"
scp -r plugins ubuntu@tencentyun:~/antileaf-nonebot
# scp -r images ubuntu@tencentyun:~/antileaf-nonebot

echo
echo "----- DONE -----"