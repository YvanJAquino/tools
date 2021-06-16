# Context Writers: Batch writing in long running processes **for humans**.

Warehousing cloud-native data from API calls is an IO bound process.  There is inbound IO from making web service calls and outbound IO from ... making more web service calls to move the data back into your data warehouse.

Warehousing large batches in a serial fashion  means the ingest process needs to stop whatever it's doing, send the data, and wait for a response that could take a good amount of time.  The warehouse's client library might make this a bit easier by moving the load job to a separate thread; it means the developer would need to manage those threads and for inexperienced data workers it means they're probably going to thread-sync right after the load job.  

Say the load batching is being done the right way already.  If you're doing that in your driver code, it's impacting readability because batching inline is ugly.  Luckily, batching and batch management is a really good use case for context-based management:

1. Load batching is generally consistent in that it happens in specific sized chunks or after some limit has been met.
2. Load batching happens intermittently and as a result of (1) - but it also needs to happen one last time if you haven't hit the limit and you still have data.  
3. The code that handles the batching happens in a repeatable and consistent manner.  
4. If the load job happens on a separate thread, those threads need to be sync'ed and terminated gracefully.  Assuming the batch job's kinks have been worked out, the synchronization of threads should happen in a way that doesn't interrupt the ingest process.

```
with ContextBatchWriter(**my_params) as cbw:
  for batch in my_data_process():
    cbw + batch
```
