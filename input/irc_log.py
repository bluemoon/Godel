import glob
import os
class irc_logParser:
    def loadLogs(self, data, limit=None):
        "accepts data as a glob pattern"
        files    = {}
        output   = []
        
        files = glob.glob(data)
        total_bytes = 0
        line_count  = 0
        
        for _file in files:
            total_bytes = total_bytes + os.path.getsize(_file)
            fhandle = open(_file)
            source_data = fhandle.readlines()
            for c in source_data:    
                data =  c[20:-1]
                if not data:
                    pass
                elif data[0] == '<':
                    userstring = data[1:].split('>')
                    username = userstring[0]
                    string =   userstring[1:]
                    if len(string) > 1:
                        string = ' '.join(string)
                
                    text = str(string[0][1:])

                    output.append(text)

                line_count += 1
                if limit:
                    if line_count >= limit:
                        return output
                
            ## end: for _file in files    
            fhandle.close()
        print 'log bytes: %d' % total_bytes
        return output
