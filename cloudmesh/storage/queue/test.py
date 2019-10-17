from cloudmesh.storage.queue.StorageQueue import StorageQueue

queue = StorageQueue("storage_a", "storage_b", name="simple")

queue.copy_file("~/a/1/x", "~/b")


queue.copy_tree(".", ".")


m,f = queue.get_actions()

print ('----')
print (m)
print ('----')
print (f)

queue.run()

