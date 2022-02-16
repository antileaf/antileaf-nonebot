# ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/plugins"
scp -r -f -l 8192 plugins ubuntu@tencentyun:~/antileaf-nonebot
# scp -r images ubuntu@tencentyun:~/antileaf-nonebot

echo
echo "----- DONE -----"