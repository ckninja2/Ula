import sys

if sys.argv[1] == 'ubuntu-latest':
  print('running on linux')
elif sys.argv[1] == 'windows-latest':
  print('running in windows')
  
