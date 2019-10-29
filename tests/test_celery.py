from app.task.celery_task import add_together, print_hello

result = add_together.delay(11, 37)
# 等待任务完成, 返回任务执行结果.
print(result.wait())
# 获取任务执行结果
print(result.get())

print_hello.delay()
print('celery print_hello')

