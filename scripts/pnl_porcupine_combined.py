#!/usr/bin/env python
import sys
import nipype
import nipype.pipeline as pe
import nipype.interfaces.utility as utility
sys.path.append('/home/tb571/Documents/pnlNipype/scripts')
import function_wrappers
import nipype.interfaces.io as io

#tashrif inserted
from os.path import join as pjoin
from conversion import read_cases

NCPU = 16
bet_threshold = '0.25'
bids_data_dir = '/home/tb571/Downloads/INTRuST_BIDS/'
bids_derivatives = pjoin(bids_data_dir,'derivatives','pnlNipype')
cases = read_cases(pjoin(bids_data_dir, 'caselist.txt'))
cases = '003GNX007'
graph_type = 'orig'
overwrite = False
pipe_out_dir = '/tmp/dwi_pipeline'
ukf_params = '--seedingThreshold,0.4,--seedsPerVoxel,1'

#Basic interface class generates identity mappings
NodeHash_20723a0 = pe.Node(utility.IdentityInterface(fields=['subject_id','ukf_params','bet_threshold','outDir','ncpu']), name = 'NodeName_20723a0')
NodeHash_20723a0.inputs.subject_id = cases
NodeHash_20723a0.inputs.ukf_params = ukf_params
NodeHash_20723a0.inputs.bet_threshold = bet_threshold
NodeHash_20723a0.inputs.outDir = bids_derivatives
NodeHash_20723a0.inputs.ncpu = NCPU
##tashrif inserted##
#NodeHash_20723a0.iterables=[('subject_id', cases)]

#Custom interface wrapping function inter_outputs
NodeHash_20c3840 = pe.Node(interface = function_wrappers.inter_outputs, name = 'NodeName_20c3840')

#Flexibly collect data from disk to feed into workflows.
##tashrif inserted##
templates = {'dwi': 'sub-{subject}/dwi/*_dwi.nii.gz',
             'bvalFile': 'sub-{subject}/dwi/*_dwi.bval',
             'bvecFile': 'sub-{subject}/dwi/*_dwi.bvec'}
NodeHash_1ac2950 = pe.Node(io.SelectFiles(templates=templates, base_directory= bids_data_dir), name = 'NodeName_1ac2950')
NodeHash_1ac2950.inputs.base_directory = bids_data_dir



#Custom interface wrapping function dwi_align
NodeHash_1c9fb00 = pe.Node(interface = function_wrappers.dwi_align, name = 'NodeName_1c9fb00')

#Custom interface wrapping function pnl_eddy
NodeHash_1cd0d10 = pe.Node(interface = function_wrappers.pnl_eddy, name = 'NodeName_1cd0d10')

#Custom interface wrapping function dwi_bet_mask
NodeHash_147fc50 = pe.Node(interface = function_wrappers.dwi_bet_mask, name = 'NodeName_147fc50')

#Custom interface wrapping function ukf_tract
NodeHash_37a74f0 = pe.Node(interface = function_wrappers.ukf_tract, name = 'NodeName_37a74f0')

#Create a workflow to connect all those nodes
analysisflow = nipype.Workflow('MyWorkflow', base_dir=pipe_out_dir)
analysisflow.connect(NodeHash_20723a0, 'subject_id', NodeHash_1ac2950, 'subject')
analysisflow.connect(NodeHash_1ac2950, 'bvecFile', NodeHash_1c9fb00, 'bvec_file')
analysisflow.connect(NodeHash_1ac2950, 'bvalFile', NodeHash_1c9fb00, 'bval_file')
analysisflow.connect(NodeHash_1ac2950, 'dwi', NodeHash_1c9fb00, 'img_file')
analysisflow.connect(NodeHash_20723a0, 'ncpu', NodeHash_1cd0d10, 'nproc')
analysisflow.connect(NodeHash_20723a0, 'bet_threshold', NodeHash_147fc50, 'bet_threshold')
analysisflow.connect(NodeHash_20723a0, 'ukf_params', NodeHash_37a74f0, 'givenParams')
analysisflow.connect(NodeHash_20723a0, 'subject_id', NodeHash_20c3840, 'id')
analysisflow.connect(NodeHash_20723a0, 'outDir', NodeHash_20c3840, 'dir')
analysisflow.connect(NodeHash_20c3840, 'eddy_tract_prefix', NodeHash_37a74f0, 'out')
analysisflow.connect(NodeHash_20c3840, 'eddy_prefix', NodeHash_1cd0d10, 'out')
analysisflow.connect(NodeHash_1cd0d10, 'out_bvec', NodeHash_37a74f0, 'bvecFile')
analysisflow.connect(NodeHash_1cd0d10, 'out_bval', NodeHash_37a74f0, 'bvalFile')
analysisflow.connect(NodeHash_1cd0d10, 'out_dwi', NodeHash_37a74f0, 'dwi')
analysisflow.connect(NodeHash_147fc50, 'dwi_mask', NodeHash_37a74f0, 'dwimask')
analysisflow.connect(NodeHash_20c3840, 'eddy_bse_betmask_prefix', NodeHash_147fc50, 'out')
analysisflow.connect(NodeHash_1c9fb00, 'out_bval', NodeHash_147fc50, 'bval_file')
analysisflow.connect(NodeHash_1c9fb00, 'out_img', NodeHash_147fc50, 'img')
analysisflow.connect(NodeHash_1c9fb00, 'out_bvec', NodeHash_1cd0d10, 'bvecFile')
analysisflow.connect(NodeHash_1c9fb00, 'out_bval', NodeHash_1cd0d10, 'bvalFile')
analysisflow.connect(NodeHash_1c9fb00, 'out_img', NodeHash_1cd0d10, 'dwi')
analysisflow.connect(NodeHash_20c3840, 'dwi_align_prefix', NodeHash_1c9fb00, 'out_prefix')

#Run the workflow
#plugin = 'MultiProc' #adjust your desired plugin here
#plugin_args = {'n_procs': 1} #adjust to your number of cores
analysisflow.write_graph(graph2use='flat', format='png', simple_form=False)
#analysisflow.run(plugin=plugin, plugin_args=plugin_args)
analysisflow.run()
