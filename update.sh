ssh ubuntu@tencentyun "rm -r -f ~/antileaf-nonebot/plugins"
scp -r plugins ubuntu@tencentyun:~/antileaf-nonebot/plugins

echo
echo "----- DONE -----"