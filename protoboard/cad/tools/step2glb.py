"""STEP -> GLB with the assembly tree, names and colours (OpenCascade XCAF + RWGltf_CafWriter).

Usage: python step2glb.py <in.stp> <out.glb> [linear_deflection_mm=0.5]
Run with the stack's CAD runtime (.protoboard/tools/cad/bin/python). Output in metres, Y up (glTF).
"""
import sys
import time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.RWGltf import RWGltf_CafWriter
from OCP.collections import IndexedDataMap_TCollection_AsciiString_TCollection_AsciiString as IndexMap
from OCP.Message import Message_ProgressRange
from OCP.IFSelect import IFSelect_RetDone
from OCP.RWMesh import RWMesh_CoordinateSystem

src, dst = sys.argv[1], sys.argv[2]
defl = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
t0 = time.time()
doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
reader = STEPCAFControl_Reader()
reader.SetNameMode(True)
reader.SetColorMode(True)
if reader.ReadFile(src) != IFSelect_RetDone:
    sys.exit("read failed")
reader.Transfer(doc)
print(f"read {time.time()-t0:.0f}s", flush=True)
# the reader's combined shape shares its TShapes with the document labels, so meshing it
# puts the triangulation where the glTF writer reads it
BRepMesh_IncrementalMesh(reader.Reader().OneShape(), defl, False, 0.5, True)
print(f"meshed {time.time()-t0:.0f}s", flush=True)
w = RWGltf_CafWriter(TCollection_AsciiString(dst), True)
w.ChangeCoordinateSystemConverter().SetInputLengthUnit(0.001)
w.ChangeCoordinateSystemConverter().SetInputCoordinateSystem(RWMesh_CoordinateSystem.RWMesh_CoordinateSystem_Zup)
w.Perform(doc, IndexMap(), Message_ProgressRange())
print(f"wrote {dst} {time.time()-t0:.0f}s", flush=True)
