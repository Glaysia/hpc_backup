# import pandas as pd
# import numpy as np
import os
from ansys.aedt.core.maxwell import Maxwell3d 
from ansys.aedt.core.desktop import Desktop
from ansys.aedt.core.modules.material import Material
import argparse
# import math
# import shutil
# import time
# import matplotlib.pyplot as plt
# import pandas as pd
# $ pip install numpy matplotlib pandas pyansys==2025.1.3
class HW3():
    def __init__(self, proj_name:str = 'eddy'): # 일단, 프로젝트명에 _ 를 넣지 마세요

        self.DT : Desktop \
            = Desktop(version="2024.2", non_graphical=True, student_version=False)
        self.DT.disable_autosave()                          # type: ignore

        sol_type = "Transient"
        self.M3D :Maxwell3d \
            = Maxwell3d(solution_type=sol_type, student_version=False)
        self.oDesign = self.M3D.odesign                     # type: ignore
        self.proj_name:str = proj_name
        self.desi_name = "eddy"
        self.pyaedtDir = os.path.dirname(os.path.abspath(__file__))

        self.initializeProjectsDirectory()
        self.proj = self.M3D.oproject                       # type: ignore
        self.M3D.rename_design(self.desi_name, save=False)  # type: ignore
        

    def initializeProjectsDirectory(self)->None:
        self.projects:list[str] = []

        if os.path.exists(
            aedt_projects_dir:=os.path.join(
                self.pyaedtDir,"../aedtProjects"
                )
            ):
            self.projects = os.listdir(aedt_projects_dir)
        else:
            os.mkdir(aedt_projects_dir)

        self.aedt_project_dir = aedt_projects_dir

        flag = True
        while flag:
            if os.path.exists(os.path.join(self.aedt_project_dir, self.proj_name)):
                if len(_:=self.proj_name.split("_"))==1:
                    self.proj_name= _[0]+"_1"
                else:
                    self.proj_name= _[0]+f"_{int(_[1])+1}"

                print(f"프로젝트명 변경: {self.proj_name}")
            else:
                flag = False

        os.mkdir(_:=os.path.join(self.aedt_project_dir, self.proj_name))
        self.file = (os.path.join(os.path.abspath(_),f"{self.proj_name}.aedt"))
        self.M3D.save_project(                              # type: ignore
            file_name= self.file
        )

    def modeling(self,metal_material:str="Copper",is_metal_20T:bool=False,is_magnet_2:bool=False):
        self.cu_material = metal_material
        self.is_cu_20T = is_metal_20T
        self.is_magnet_2 = is_magnet_2

        M3D = self.M3D
        from ansys.aedt.core.modules.material_lib import Materials
        m : Materials = M3D.materials # type: ignore
        _magnet:Material = m.duplicate_material("NdFe35", name="magnet_n")        # type: ignore
        _magnet.get_magnetic_coercivity()  # 자화 확인                               # type: ignore
        _magnet.set_magnetic_coercivity(value=-890000, x=0, y=0, z=1)  # 자화 방향 수정(+z) # type: ignore


        M3D.modeler.delete(assignment="Metal")# type: ignore
        M3D.modeler.delete(assignment="Magnet")# type: ignore
        M3D.modeler.delete(assignment="Band")# type: ignore
        from ansys.aedt.core.modeler.modeler_3d import Modeler3D
        from ansys.aedt.core.modeler.cad.object_3d import Object3d

        Metal:Object3d 
        magnet:Object3d
        band:Object3d  

        modeler:Modeler3D = M3D.modeler  # type: ignore

        region:Object3d = modeler.create_region(pad_value=[500,500,500,500,500,500], pad_type='Absolute Offset', name='Region') # type: ignore
        # 금속판 그리기
        zo = -10 if is_metal_20T else 0
        zs =  20 if is_metal_20T else 10
        origin = [0, 0, zo]
        sizes = [200, 150, zs]
        Metal:Object3d  = modeler.create_box(origin, sizes, name="Metal", material=metal_material) # type: ignore

        # 막대 자석 그리기
        origin = [80, 0, 10]
        sizes = [20, 40, 10 if is_magnet_2 else 5]
        magnet:Object3d = modeler.create_box(origin, sizes, name="Magnet", material="magnet_n")# type: ignore
        modeler.move(magnet,[10,0,0.1]) # type: ignore
        # band 그리기(움직이는 물체를 감싸는 형태로 만들어줘야 한다)
        origin:list[float] = [-1, -1, 10.05]
        sizes:list[float] = [42, 152, 10.1]
        band:Object3d = modeler.create_box(origin, sizes, name="Band", material="Vacuum")# type: ignore
        modeler.move(band,[80,0,0]) # type: ignore

        self.Metal:Object3d  = Metal
        self.magnet:Object3d  = magnet
        self.band:Object3d  = band

    def set_setup(self,v:float):
        self.velocity = v
        from ansys.aedt.core.modules.solve_setup import Setup

        setup:Setup = self.M3D.create_setup(name='MySetupAuto', setup_type="Transient")  # type: ignore
        props:dict = setup.props            # type: ignore
        
        props["StopTime"]="1s"
        props["TimeStep"]="75ms"
        props["SaveFieldsType"]="Every N Steps"
        props["N Steps"]="1s"
        props["Steps From"]="0s"
        props["Steps To"]="1s"

        M3D = self.M3D
        from ansys.aedt.core.modules.mesh import Mesh, MeshOperation



        mesh:Mesh = M3D.mesh    # type: ignore
        meshing: MeshOperation
        meshing = mesh.assign_length_mesh(["Magnet"], inside_selection=True, maximum_length=10, maximum_elements=None, name="Mesh1") # type: ignore
        meshing = mesh.assign_length_mesh(["Metal"], inside_selection=True, maximum_length=(10 if self.is_magnet_2 else 5), maximum_elements=None, name="Mesh2")   # type: ignore
        meshing = mesh.assign_length_mesh(["Band"], inside_selection=True, maximum_length=10, maximum_elements=None, name="Mesh3")   # type: ignore

        self.meshing:MeshOperation = meshing

        velocity=f"{v}cm_per_sec"
        self.Motionsetup=M3D.assign_translate_motion("Band", coordinate_system='Global', axis='Y', positive_movement=True, start_position=0, periodic_translate=False, negative_limit=0, # type: ignore
                                                positive_limit=110, velocity=velocity, mechanical_transient=False, mass=0, damping=0, load_force=0, motion_name="Motionsetup")
        
        effect:bool =M3D.eddy_effects_on(self.Metal, enable_eddy_effects=True, enable_displacement_current=True)  # type: ignore
        self.setup:Setup = setup

    def analyze(self):
        self.M3D.save_project(self.file)    # type: ignore
        self.setup.analyze()                # type: ignore  
        self.M3D.save_project(self.file)    # type: ignore

    def makeResult(self):
        plot_name = f"magnet{2 if self.is_magnet_2 else 1}_{20 if self.is_cu_20T else 10}T_{self.cu_material}_{self.velocity}cm_per_sec"
        self.plot_name = f"{self.proj_name}_{plot_name}"
        from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D
        post:PostProcessor3D = self.M3D.post # type: ignore
        success:bool = post.create_report(   # type: ignore
            # 필드 계산기에서 생성한 Named Expression
            expressions=["SolidLoss"],
            report_category="Loss",
            context="Field_Line",
            plot_type="Rectangular plot",         # 표 형식으로 결과를 출력
            primary_sweep_variable="Time",
            plot_name= self.plot_name    # 보고서 이름
        )

    def makeCSV(self, csv_dir:str = "/home1/harry261/Documents/csv"):
        from ansys.aedt.core.visualization.post.post_common_3d import PostProcessor3D
        post:PostProcessor3D = self.M3D.post    # type: ignore
        csv = post.export_report_to_csv(        # type: ignore
                plot_name=self.plot_name, project_dir=csv_dir)
        print(f"csv 파일 생성:{csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metal-material", type=str, required=True)
    parser.add_argument("--metal-thick", type=str, required=True)
    parser.add_argument("--magnet-n", type=str, required=True)
    parser.add_argument("--velocity", type=str, required=True)
    parser.add_argument("--project-name", type=str, required=True)
    parser.add_argument("--csv-dir", type=str, required=True)
    args = parser.parse_args()

    metal_material  = args.metal_material
    is_metal_20T    = (args.metal_thick=='True')
    is_magnet_2     = (args.magnet_n=='2')
    velocity        = args.velocity
    proj_name       = args.project_name
    csv_dir         = args.csv_dir

    hw3:HW3 = HW3(proj_name)
    hw3.modeling(metal_material=metal_material, is_metal_20T=is_metal_20T, is_magnet_2=is_magnet_2)
    hw3.set_setup(v=velocity)
    hw3.analyze()
    hw3.makeResult()
    hw3.makeCSV(csv_dir)

    pass