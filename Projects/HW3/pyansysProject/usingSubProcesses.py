import subprocess
import numpy as np
from typing import List, Tuple
from time import sleep
import os

# 부모 환경 복사
env = os.environ.copy()
env['ANSYSLMD_LICENSE_FILE'] = '1055@172.16.10.81'


csv_dir = "/home1/harry261/Documents/csv"

idx_bools: List[List[bool]] = [list(map(lambda x: x == '1', format(i, '03b'))) for i in range(8)]  # type: ignore
idx_material: List[List] = []
for bits in idx_bools:
    entry = [
        "Brass" if bits[0] else "Copper",
        "20T" if bits[1] else "10T",
        '2' if bits[2] else '1'
    ]
    idx_material.append(entry)

# velocities = [(9,15), (7,12), (7,12), (5,10), (26,45), (23,39), (23,39), (20,33)]
velocities = [(9,50) for _ in range(8)]

idx_with_velocity: List[Tuple[str, str, str, Tuple[str]]] = []
for i, material in enumerate(idx_material):
    velocity_values = tuple(map(lambda x: f"{x:.2f}", np.linspace(*velocities[i], 8)))
    new_entry = tuple(material + [velocity_values])
    idx_with_velocity.append(new_entry)

idx_final: List[Tuple[str, str, str, Tuple[str]]] = idx_with_velocity

def makeProcess(material:str, thick:str, magnet_n:str, velocity:str, idx:str)->None:
    subprocess.Popen([
        "python", "/root/projects/hpc_backup/Projects/HW3/pyansysProject/hw3.py", 
        "--metal-material", material, 
        "--metal-thick", f"{thick =='20T'}",
        "--magnet-n", magnet_n,
        "--velocity", velocity,
        "--project-name", f"pp{idx}{material}_1",
        "--csv-dir", "/root/projects/hpc_backup/Projects/HW3/pyansysProject/csv"
        ]
    ) 
print(idx_final)
# nnn = ('Brass', '10T', '1', ('22.00', '23.47', '24.95', '26.42', '27.89', '29.37', '30.84', '32.32', '33.79', '35.26', '36.74', '38.21', '39.68', '41.16', '42.63', '44.11', '45.58', '47.05', '48.53', '50.00'))

# index:int = 0
# item = nnn
# for v in item[3]:
#     makeProcess(
#         material=item[0],
#         thick=item[1],
#         magnet_n=item[2],
#         velocity=v,
#         idx=f"{index}"
#         )
#     sleep(10)

#     index+=1
# pass
# 결과 출력
index:int = 0
for item in idx_final:
    for v in item[3]:
        makeProcess(
            material=item[0],
            thick=item[1],
            magnet_n=item[2],
            velocity=v,
            idx=f"{index}"
            )
        sleep(12)
        index+=1



# 예: 두 개의 스크립트에 서로 다른 인수를 전달하는 경우
# subprocess.Popen([
#     "python", "hw3.py", 
#     "--metal-material", "Copper", 
#     "--metal-thick", f"{False}",
#     "--magnet-n", "1",
#     "--velocity", "7",
#     "--project-name", "test_1",
#     "--csv-dir", "/home1/harry261/Documents/csv"
#     ]
# )

# subprocess.Popen([
#     "python", "test.py", 
#     "--metal-material", "Copper", 
#     "--metal-thick", f"{True}",
#     "--magnet-n", "1",
#     "--velocity", "8",
#     "--project-name", "testt_2",
#     "--csv-dir", "/root/src/project1/hello"
#     ]
# )
