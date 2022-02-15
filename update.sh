ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/plugins"
scp -r plugins ubuntu@tencentyun:~/antileaf-nonebot/plugins
scp -r images ubuntu@tencentyun:~/antileaf-nonebot/images

echo
echo "----- DONE -----"