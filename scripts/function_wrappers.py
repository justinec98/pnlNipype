from nipype import Node, Function
from align import work_flow as align_wf
from pnl_eddy import work_flow as eddy_wf
from bet_mask import work_flow as bet_mask_wf
from ukf import work_flow as ukf_wf
from script_interfaces import define_outputs_wf

dwi_align= Function(input_names=['img_file', 'out_prefix', 'bval_file', 'bvec_file'],
                     output_names=['out_img','out_bval','out_bvec'],
                     function=align_wf)

pnl_eddy= Function(input_names=['dwi', 'bvalFile', 'bvecFile', 'out', 'nproc'],
                   output_names=['out_dwi', 'out_bval', 'out_bvec'],
                   function= eddy_wf)


dwi_bet_mask= Function(input_names=['img', 'bval_file', 'out', 'bet_threshold'],
                       output_names=['dwi_mask'],
                       function= bet_mask_wf)

ukf_tract= Function(input_names=['dwi', 'dwimask', 'bvalFile', 'bvecFile', 'out', 'givenParams'],
                    output_names=['tract_file'],
                    function=ukf_wf)


inter_outputs= Function(input_names=['id','dir'],
                        output_names= ['t1_align_prefix', 't2_align_prefix', 'dwi_align_prefix',
                        't1_mabsmask_prefix','t2_mabsmask_prefix', 'eddy_bse_betmask_prefix',
                        'fs_dir', 'fs_in_eddy', 'fs_in_epi',
                        'eddy_bse_prefix', 'eddy_bse_masked_prefix', 'eddy_epi_bse_prefix', 'eddy_epi_bse_masked_prefix',
                        'eddy_prefix', 'eddy_epi_prefix',
                        'eddy_tract_prefix','eddy_epi_tract_prefix',
                        'eddy_fs2dwi_dir', 'epi_fs2dwi_dir',
                        'eddy_wmql_dir', 'eddy_wmqlqc_dir', 'epi_wmql_dir', 'epi_wmqlqc_dir'],
                        function= define_outputs_wf)

