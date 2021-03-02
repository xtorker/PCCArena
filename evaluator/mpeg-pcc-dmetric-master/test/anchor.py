#!/usr/bin/python
import os
import collections
import sys
import getopt
import ConfigParser

org = {}
norm = {}
bitstreamPre = {}
decodedPre = {}
log = {}
gRange = {}
cRange = {}
pPSNR = {}
numa = {}
numb = {}
seqSet = []
calc = '/data3/tian/quality/pcc_quality/test/pc_error_0.09'  # Specify the program of the distortion calculator


def tree():
  return collections.defaultdict(tree)


def getFloatValue( line, keyword ):
  flag = 0
  value = 0.0
  if keyword in line:
    for token in line.split():
      try:
        if float(token):
          flag = 1
          value = float(token)
      except ValueError:
        continue
  return flag, value


def getResults( keyword, logfile ):
  ret = 0.0
  with open( logfile ) as inf:
    for line in inf:
      line = line.strip()
      if keyword in line:
        flag, value = getFloatValue( line, keyword )
        if flag:
          ret = value
  return ret


def usage():
  print('./anchor -c config.ini <-r> <-h> <-d data>')


def getSetFromString( str, separator ):
  if separator == " ":
    ret = str.split()
  else:
    str = ''.join(str.split())
    ret = str.split( separator )
  return ret


def ConfigSectionMap( section ):
  numa[section] = ''
  numb[section] = ''
  pPSNR[section] = ''
  options = Config.options( section )
  for option in options:
    if option == "org":
      org[section] = Config.get( section, option )
    elif option == "norm":
      norm[section] = Config.get( section, option )
    elif option == "bitstream":
      bitstreamPre[section] = Config.get( section, option )
    elif option == "decoded":
      decodedPre[section] = Config.get( section, option )
    elif option == "log":
      log[section] = Config.get( section, option )
    elif option == "grange":
      strtmp = Config.get( section, option )
      gRange[section] = map( int, getSetFromString( strtmp, ',' ) )
    elif option == "crange":
      strtmp = Config.get( section, option )
      cRange[section] = map(int, getSetFromString( strtmp, ',' ) )
    elif option == "ppsnr":
      pPSNR[section] = float( Config.get( section, option ) )
    elif option == "numa":
      numa[section] = int( Config.get( section, option ) )
    elif option == "numb":
      numb[section] = int( Config.get( section, option ) )


def main(argv):
  ##########################################
  # Tune this section on what you want to do
  ##########################################
  runCmd = 0                      # Set to 1 to run evaluation. Set to 0 to put the Excel sheet ready output and no evaluation would be actually called
  myIni = ""
  seqSetSpecial = ""
  bSort = 0

  # Update the variables from command line
  try:
    opts, args = getopt.getopt(argv, "hrd:c:s", ["help", "run", "data=", "config=", "sort"])
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt in ("-d", "--data"):
      seqSetSpecial = [arg]
    elif opt in ("-r", "--run"):
      runCmd = 1
    elif opt in ("-c", "--config"):
      myIni = [arg]
    elif opt in ("-s", "--sort"):
      bSort = 1

  if myIni == "":
    usage()
    sys.exit(2)

  # Load configurations
  Config.read(myIni)
  seqSet = Config.sections()
  # print("sections: %s" % seqSet)

  if seqSetSpecial != "":
    seqSet = seqSetSpecial

  if bSort == 1:
    seqSet = sorted( seqSet )

  for seq in seqSet:
    ConfigSectionMap( seq )

  # Do evaluations and reporting
  for seq in seqSet:
    data = tree()
    # Do evaluations
    for g in gRange[seq]:
      for c in cRange[seq]:
        if ( numa[seq] == '' ):  # Static case
          decoded = '%s_g%d_c%d.ply'      % ( decodedPre[seq], g, c )
          logfile = '%s_g%d_c%d_psnr.txt' % ( log[seq], g, c )

          bExist = os.path.isfile(decoded)
          if bExist:
            if norm[seq]:
              if pPSNR[seq] == '':
                cmd = 'date; %s -a %s -b %s -n %s -c       > %s; date' % (calc, org[seq], decoded, norm[seq],             logfile)
              else:
                cmd = 'date; %s -a %s -b %s -n %s -c -r %f > %s; date' % (calc, org[seq], decoded, norm[seq], pPSNR[seq], logfile)
            else:
              if pPSNR[seq] == '':
                cmd = 'date; %s -a %s -b %s -c       > %s; date' % (calc, org[seq], decoded,             logfile)
              else:
                cmd = 'date; %s -a %s -b %s -c -r %f > %s; date' % (calc, org[seq], decoded, pPSNR[seq], logfile)
            if runCmd:
              print('%s' % (cmd) )
              os.system(cmd)
            c2c = getResults( 'mseF,PSNR (p2point):', logfile )
            c2p = getResults( 'mseF,PSNR (p2plane):', logfile )
            y   = getResults( 'c[0],PSNRF         :', logfile )
            u   = getResults( 'c[1],PSNRF         :', logfile )
            v   = getResults( 'c[2],PSNRF         :', logfile )
            if runCmd:
              print( '%s -> %f, %f' % (logfile, c2c, c2p) )
            data[g][c]['c2c'] = c2c
            data[g][c]['c2p'] = c2p
            data[g][c]['y'  ] = y
            data[g][c]['u'  ] = u
            data[g][c]['v'  ] = v
          else:
            print('Not found file %s' % ( decoded ) )
            return
            # data[g][c]['c2c'] = -99.12345
            # data[g][c]['c2p'] = -99.67890
            # data[g][c]['y'  ] = -99.99
            # data[g][c]['u'  ] = -99.99
            # data[g][c]['v'  ] = -99.99

        else:                   # Dynamic case
          dataLocal = tree()
          dataLocal['c2c'] = []
          dataLocal['c2p'] = []
          dataLocal['y'  ] = []
          dataLocal['u'  ] = []
          dataLocal['v'  ] = []

          seqN = seq.replace('AllI','')
          for frm in range(numa[seq], numb[seq]+1):
            fname = '%s%04d.ply'   % (org[seq],  frm)
            nname = '%s%04d_n.ply' % (norm[seq], frm)
            if "AllI" not in seq:
              decoded  = '%s/%s/%s_GOP2_g%d/%s_GOP2_g%d/%s_%d_g%d_c%d.ply'    % ( decodedPre[seq],   seqN, seqN, g, seqN, g, seqN, frm, g, c )
            else:
              decoded  = '%s/%s/%s_I_g%d/%s_I_g%d/%s_%d_g%d_c%d.ply'          % ( decodedPre[seq],   seqN, seqN, g, seqN, g, seqN, frm, g, c )
            logfile   = '%s_%04d_g%d_c%d_psnr.txt' % ( log[seq], frm, g, c )

            bExist = os.path.isfile(decoded)
            if bExist:
              if norm[seq]:
                if pPSNR[seq] == '':
                  cmd = 'date; %s -a %s -b %s -n %s -c       > %s; date' % (calc, fname, decoded, nname,             logfile)
                else:
                  cmd = 'date; %s -a %s -b %s -n %s -c -r %f > %s; date' % (calc, fname, decoded, nname, pPSNR[seq], logfile)
              else:
                if pPSNR[seq] == '':
                  cmd = 'date; %s -a %s -b %s -c       > %s; date' % (calc, fname, decoded,             logfile)
                else:
                  cmd = 'date; %s -a %s -b %s -c -r %f > %s; date' % (calc, fname, decoded, pPSNR[seq], logfile)
              if runCmd:
                print('%s' % (cmd) )
                os.system(cmd)
              c2c = getResults( 'mseF,PSNR (p2point):', logfile )
              c2p = getResults( 'mseF,PSNR (p2plane):', logfile )
              y   = getResults( 'c[0],PSNRF         :', logfile )
              u   = getResults( 'c[1],PSNRF         :', logfile )
              v   = getResults( 'c[2],PSNRF         :', logfile )
              if runCmd:
                print( '%s -> %f, %f' % (logfile, c2c, c2p) )
              dataLocal['c2c'].append( c2c )
              dataLocal['c2p'].append( c2p )
              dataLocal['y'  ].append( y )
              dataLocal['u'  ].append( u )
              dataLocal['v'  ].append( v )
            else:
              print('Not found file %s' % ( decoded ) )
              return

          data[g][c]['c2c'] = sum( dataLocal['c2c'] ) / len( dataLocal['c2c'] )
          data[g][c]['c2p'] = sum( dataLocal['c2p'] ) / len( dataLocal['c2p'] )
          data[g][c]['y'  ] = sum( dataLocal['y'  ] ) / len( dataLocal['y'  ] )
          data[g][c]['u'  ] = sum( dataLocal['u'  ] ) / len( dataLocal['u'  ] )
          data[g][c]['v'  ] = sum( dataLocal['v'  ] ) / len( dataLocal['v'  ] )

    # Do reporting
    #print('')
    #print('%s point2point point2plane y u v' % (seq))

    # print('pj = %s' % (pj) )
    for c in cRange[seq]:
      # print('c = %s' % (c) )
      for g in gRange[seq]:
        print( '%s %d  %f  %f  %f  %f  %f' % (seq, g, data[g][c]['c2c'], data[g][c]['c2p'], data[g][c]['y'], data[g][c]['u'], data[g][c]['v']) )

# Init the config variable
Config = ConfigParser.ConfigParser()
if __name__ == "__main__":
  main(sys.argv[1:])
