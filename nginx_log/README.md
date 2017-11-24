# log-analysis

---

### 日志数据分析
`nginx.conf`添加以下日志格式，并引用。
```
log_format  main  '{ "timestamp": "$time_local", '
                    '"domain": "$scheme://$host" ,'	          
                    '"cdnip": "$remote_addr",'
                    '"request_time": "$request_time" ,'
                    '"request": "$request" ,'
                    '"status": "$status" ,'  
                    '"clientip": "$http_x_forwarded_for",'
                    '"body_bytes_sent": "$body_bytes_sent" ,'
                    '"upstream_status": "$upstream_status" ,'                    
                    '"upstream_response_time": "$upstream_response_time",'  
                    '"upstream_addr": "$upstream_addr" ,'
                    '"http_user_agent": "$http_user_agent" }'  ;
```
参数|说明  
--- | ---
time_local|访问时间
scheme，host|获取域名
remote_addr|客户端地址，CDN地址
request_time|请求处理时间
request|请求URL
status|请求状态码
http_x_forwarded_for|客户端地址
body_bytes_sent|发送给客户端的字节数
upstream_status|后端状态
upstream_response_time|后端响应时间
upstream_addr|后端地址
http_user_agent|用户终端信息

#### 处理流程
通过计划任务进行切割日志并转换csv格式数据,对数据进行数据分析，获取的结果传输到mysql数据库。