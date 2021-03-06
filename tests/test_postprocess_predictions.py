# -*- coding: utf-8 -*-
"""
Tests for functionalities in orthoseg.lib.postprocess_predictions.
"""

from pathlib import Path
import sys

from geofileops import geofile

# Add path so the local orthoseg packages are found 
sys.path.insert(0, str(Path(__file__).resolve().parent / '..'))
from orthoseg.lib import postprocess_predictions as post_pred

def get_testdata_dir() -> Path:
    return Path(__file__).resolve().parent / 'data'

def test_read_prediction_file():
    # Read + polygonize raster prediction file
    pred_raster_path = get_testdata_dir() / '129568_185248_130592_186272_4096_4096_1_pred.tif'
    pred_raster_gdf = post_pred.read_prediction_file(pred_raster_path, border_pixels_to_ignore=128)
    #geofile.to_file(pred_raster_gdf, get_testdata_dir() / f"{pred_raster_path.stem}.gpkg")

    # Read the comparison file, that contains the result of the polygonize
    pred_comparison_path = get_testdata_dir() / f"{pred_raster_path.stem}.gpkg"
    pred_comparison_gdf = geofile.read_file(pred_comparison_path)

    # Now compare they are the same
    assert len(pred_raster_gdf) == len(pred_comparison_gdf)

def test_clean_vectordata(tmpdir):
    temp_dir = Path(tmpdir)

    # Clean data
    input1_path = get_testdata_dir() / '129568_184288_130592_185312_4096_4096_1_pred.gpkg'
    input2_path = get_testdata_dir() / '129568_185248_130592_186272_4096_4096_1_pred.gpkg'
    input1_gdf = geofile.read_file(input1_path)
    input2_gdf = geofile.read_file(input2_path)
    input_gdf = input1_gdf.append(input2_gdf)
    input_path = temp_dir / "vector_input.gpkg"
    geofile.to_file(input_gdf, input_path)
    output_path = temp_dir / input_path.name
    postprocess_params = {"dissolve_tiles_path": None}
    post_pred.clean_vectordata(
            input_path=input_path, 
            output_path=output_path, 
            postprocess_params=postprocess_params,
            force=True)

    # Read result and check
    geoms_simpl_filepath = output_path.parent / f"{output_path.stem}_simpl{output_path.suffix}"
    result_gdf = geofile.read_file(geoms_simpl_filepath)

    assert len(result_gdf) == 616

if __name__ == '__main__':
    # Prepare temp directory
    import tempfile
    tmp_dir = Path(tempfile.gettempdir()) / Path(__file__).stem
    print(f"tmpdir used for test: {tmp_dir}")
    if not tmp_dir.exists():
        tmp_dir.mkdir()
    tmpdir = str(tmp_dir)

    # Run!
    test_clean_vectordata(tmpdir)
    #test_read_prediction_file()
