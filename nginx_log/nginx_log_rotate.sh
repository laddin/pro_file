!/bin/bash
#nginx 日志目录
logs_path="/home/data/wwwlogs/"
#nginx 日志文件
log_name="access_log.log"
#切割时间
time_ing=`date +%Y-%m-%d`

/bin/mv ${logs_path}${log_name} ${logs_path}${time_ing}_${log_name}
/bin/kill -USR1 $(/bin/cat /var/run/nginx.pid)

find /home/data/wwwlogs/ -name "*_access_log.log" -mtime +7 |xargs -i rm -rf {}
