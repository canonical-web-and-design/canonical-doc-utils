#!/usr/bin/env python3

import subprocess
import re
import codecs

def main():
  
  outfile = codecs.open('commands.md','w', 'utf-8')

  # useful text
  pad=u'   '
  pagetext=(u"Title:Juju commands and usage\n\n"
            "# Juju Command reference\n\n"
            "You can get a list of all Juju commands by invoking `juju help\n"
            "commands` in a terminal. To drill down into each command\n"
            "use `juju help <command name>`.\n\n"
            "This same information is also provided below. Click on the\n"
            "triangle alongside a command to expand each command's entry.\n\n")

  outfile.write(pagetext)
  commands = subprocess.check_output(['juju', 'help', 'commands']).splitlines()

  for c in commands:
      
      header = '^# '+c.split()[0].decode('utf-8')+ '\n\n'
      htext = subprocess.check_output(['juju', 'help', c.split()[0].decode('unicode_escape')])
      htext = htext.decode('utf-8')
      #p = re.compile(u'Usage:(.+?)\n\nSummary:\n(.+?)\n\nOptions:\n(.+?)Details:\n(.+)', re.DOTALL)
      #h=re.findall(p, htext.decode('unicode_escape'))
      
      # search for Aliases section
      # if it exists, truncate details and process
      q= re.compile(u'Aliases: ?(.+?)$',re.DOTALL | re.IGNORECASE)
      x = re.search( q, htext)
      if x:
        match=htext[x.start()+8:].split(' ')
        htext=htext[:x.start()] # truncate the bit we matched
        alias=pad+'**Aliases:**\n\n'
        for line in match:
          if (line !=''):
            alias = alias+pad+'`'+line.strip()+'`\n\n'
      else:
        alias=u''
  
      # search for see also section
      # if it exists, truncate details and process
      q= re.compile(u'See also: ?\n(.+?)$',re.DOTALL | re.IGNORECASE)
      x = re.search( q, htext)
      if x:
        match=htext[x.start()+11:].split('\n')
        htext=htext[:x.start()] # truncate the bit we matched
        also=pad+'**See also:**\n\n'
        
        for line in match:
          if (line !=''):
            if not (type(line) == str):
              item = line.strip().decode('utf-8')
            else:
              item = line.strip()
            also = also+pad+'['+item+'](#'+item+') , \n'
        also = also[:-3]+' \n\n'
      else:
        also=u''    
      
      # search for Examples section
      # if it exists, truncate details and process
      q= re.compile(u'Examples: ?\n(.+?)$',re.DOTALL)
      x = re.search( q, htext)
      if x:
        match=htext[x.start()+10:].split('\n')
        htext=htext[:x.start()] # truncate the bit we matched
        examples=pad+'**Examples:**\n\n'
        
        for line in match:
          if (line !=''):
            if (line[0]==' '):
              examples=examples+pad
              pass
            examples = examples+pad+line+'\n'
        examples = examples+'\n\n'
      else:
        print("WARNING: {} has no examples!".format(c.split()[0]))
        examples = u''

      #process the rest of details section.
      q= re.compile(u'Details:\n(.+?)$',re.DOTALL)
      x = re.search( q, htext)
      if x:
        match=htext[x.start()+9:].split('\n')
        htext=htext[:x.start()] # truncate the bit we matched
        details=pad+'\n   **Details:**\n\n'
        section=u''
        iflag=False
        for line in match:
          if (line !=''):
            if (line[0]==' '):
              line= pad+pad+line
              iflag=True
            elif iflag:
              line= '\n'+pad+line
              iflag=False
            if ((len(line)<70) & ((line[-1:]=='.') | (line[-1:]==':'))):
              line=line+'\n'
            if (type(line) == str):
              section = section+'\n'+pad + line
            else:
              section = section+'\n'+pad + line.decode('utf8','ignore')
        details= details+section+'\n\n'
        # unpleasantness to get around silly wWindows paths in text
        if (c.split()[0] == b'autoload-credentials'):
          details = details.replace('\x07','\\a')
          details = details.replace('\\','\\\\')
          
      else:
        print("**SEVERE WARNING**: {} has no DETAILS!".format(c.split()[0]))
        details=''
      
      # generate options

      q= re.compile(u'\nOptions:\n(.+?)$',re.DOTALL)
      x = re.search( q, htext)
      if x:
        match=htext[x.start()+10:].split('\n')
        htext=htext[:x.start()] # truncate the bit we matched
        options=pad+'**Options:**\n\n'
        for line in match:
          if (line !=''):
            if (line[0]=='-'):
              options = options+pad+"_"+line.strip()+"_\n\n"
            else:
              options = options+pad+line.strip()+"\n\n"
        if not (type(options) == str):
          options = options.decode('utf-8')
      else:
        print("**SEVERE WARNING**: {} has no Options!".format(c.split()[0]))
        options=''
      options=str(options).replace('<','&lt;')
      options.replace('>','&gt;')
      # get usage and summary
      q= re.compile(u'Usage:(.+?)\n\nSummary:\n(.+?)$',re.DOTALL)
      x = re.search( q, htext)    
#      usage=pad+"**Usage:** `"+x.groups()[0].decode('utf-8')+"`\n\n"
      usage=pad+"**Usage:** `"+x.groups()[0]+"`\n\n"

      if (c.split()[0] == b'add-storage'):
        usage = "    **Usage:** ` juju add-storage [options] <unit name> <charm storage name>[=<storage constraints>] ... `\n\n"
#      summary=pad+"**Summary:**\n\n"+pad+x.groups()[1].decode('utf-8')+"\n\n"
      summary=pad+"**Summary:**\n\n"+pad+x.groups()[1]+"\n\n"
      outfile.write(header+usage+summary+options+details+examples+also+alias+'\n\n')


  outfile.close()
if __name__ == '__main__':
    main()
