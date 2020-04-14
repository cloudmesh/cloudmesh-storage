#test_gdrive3.py in cloudmesh-storage repository
from cloudmesh.storage.provider.parallelgdrive.Provider import Provider
p = Provider(service='gdrive')
# p.list(source='pictures', dir_only=False, recursive=False) # works only for recursive=False)
p.list(source='sub_cloud2', dir_only=False, recursive=False)

# p.delete(filename='sub_cloud2', recursive=True) # works for recursive=True.  Delete subdir even when recursive=False

# Not working correctly for recursive=False.  Treating it as True and deletes subdir and contents in subdir
# p.delete(filename='pictures', recursive=False) # works

# p.create_dir(directory='gdrive_kids2/pictures') # works
# p.download_file(source='C:/Users/sara/cm', file_id='19HOJUgkjRPlIFn9daaRk4BE08AkfMRUP',
#                  file_name='IU2', mime_type='image/jpeg') # works
# p.download_file(source='C:/Users/sara/cm', file_id='1aqT2cHkCS7oTqTBHIgV4Vaazyza0j2GL',
#                 file_name='gifts_downloaded_to_local',
#                 mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document') # works

# p.download_file(source='C:/Users/sara/local_pictures', file_id='1h_P9aOsrvvl33-yBZ1CPZBR3VnoXdH-S',
#                 file_name='pictures',
#                 mime_type='application/vnd.google-apps.folder') # fine.  Download works with files only

# p.download_file(source='C:/Users/sara/Emps2', file_id='1QKmP3N4nTtSDQrpsmZQi_aihfWQJ2H0J',
#                 file_name='hello2.pdf',
#                 mime_type='application/pdf') # works

# p.search(filename='schools3.xlsx', recursive=False) # works now.  Fixed issue of printing other files or folders too

# p.put(source='C:/Users/sara/gdrive_dir/gifts.docx', destination='gdrive_cloud/gifts.docx', recursive=False) # created dir but not put files
# p.put(source='C:/Users/sara/gdrive_dir/gifts.docx', destination='gdrive_cloud', recursive=False) # works for recursive=False

# Not working for recursive=True
# p.put(source='C:/Users/sara/new_emp', destination='sub_cloud3', recursive=True) # not getting subdir when recursive=True

# Fixed download's issue of adding another extension.
# p.get(source='C:/Users/sara/new_emp', destination='schools3.xlsx', recursive=False) # works for single files

# Fixed now for recursive=False, and no sub folders. recursive=True still not working
# p.get(source='C:/Users/sara/new_emp', destination='gdrive_cloud', recursive=False) # Fixed now for recursive=False

# p.get(source='C:/Users/sara/new_emp', destination='sub_cloud2', recursive=False) # recursive=True not working

p.search(filename='schools2.xlsx', recursive=False) # works now.  Fixed issue of printing other files or folders too
