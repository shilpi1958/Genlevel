### Script to submit Condor jobs for LHE event generation at UCSD

import os
import sys
import argparse

def submitCondorJob(proc, executable, options, infile, label, outputToTransfer=None, submit=False, isGridpackJob=False):
    logDir = ['Log','output','error']#os.path.join("logs",proc)

    subfile = "condor_"+proc +"_"+label+".cmd"
    f = open(subfile,"w")
    f.write("Universe = vanilla\n")
    #f.write("Grid_Resource = condor cmssubmit-r1.t2.ucsd.edu glidein-collector.t2.ucsd.edu\n")
    # f.write("x509userproxy={0}\n".format(proxy))
    # f.write("+DESIRED_Sites=\"T2_US_UCSD\"\n")
    if isGridpackJob :
        f.write("+request_cpus=8\n")
    f.write("Executable = "+executable+"\n")
    f.write("arguments =  "+(' '.join(options))+"\n")
    f.write("Transfer_Executable = True\n")
    f.write("should_transfer_files = YES\n")
    f.write("transfer_input_files = "+infile+"\n")
    if outputToTransfer is not None:
        f.write("transfer_Output_files = "+outputToTransfer+"\n")
        f.write("WhenToTransferOutput  = ON_EXIT\n")
    f.write("Notification = Never\n")
    f.write("Log=%s/gen_%s_%s.log.$(Cluster).$(Process)\n"%(logDir[0], proc, label))
    f.write("output=%s/gen_%s_%s.out.$(Cluster).$(Process)\n"%(logDir[1], proc, label))
    f.write("error=%s/gen_%s_%s.err.$(Cluster).$(Process)\n"%(logDir[2], proc, label))
    f.write("queue 1\n")
    f.close()

    cmd = "condor_submit "+subfile
    print cmd
    submit_=False
    if submit_:
        os.system(cmd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('proc', help="Names of physics model")
    parser.add_argument('--in-file', '-i', dest='infile', help="Text file containing tarballs with the path", required=True)
    parser.add_argument('--nevents', '-n', help="Number of events per job", type=int, default=10000)
    parser.add_argument('--njobs', '-j', help="Number of condor jobs", type=int, default=1)
    # parser.add_argument('--no-sub', dest='noSub', action='store_true', help='Do not submit jobs')
    # parser.add_argument('--proxy', dest="proxy", help="Path to proxy", default=os.environ["X509_USER_PROXY"])
    parser.add_argument('--rseed-start', dest='rseedStart', help='Initial value for random seed',
            type=int, default=500)
    args = parser.parse_args()

    proc = args.proc
    nevents = args.nevents
    njobs = args.njobs
    infile_txt = args.infile
    rseedStart = args.rseedStart

    os.system('mkdir -p Output_LHE'+'/'+proc+' '+'Log output error')

    #script_dir = os.path.dirname(os.path.realpath(__file__))
    executable = './runLHEJob.sh'#script_dir+'/runLHEJob.sh'
    out_dir='./Output_LHE'  #'/hadoop/cms/store/user/'+os.environ['USER']+'/mcProduction/LHE'
    for line in infile_txt:
        infile=line.rstrip()
        print "Will generate LHE events using tarball",infile

        outdir = out_dir+'/'+proc
        options = [proc, str(nevents), outdir]
        print "Options:",(' '.join(options))
        for j in range(0,njobs):
            rseed = str(rseedStart+j)
            print "Random seed",rseed
            submitCondorJob(proc, executable, options+[rseed], infile, label=rseed, submit=(not args.noSub))
