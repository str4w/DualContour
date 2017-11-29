import vtk
import numpy as np
from vtk.util.vtkConstants import *
import matplotlib.pyplot as plt

from IPython.display import Image

Red=(1,0,0)
Blue=(0,0,1)
Green=(0,1,0)
Yellow=(1,1,0)
Magenta=(1,0,1)
Cyan=(0,1,1)
Purple=(0.5,0,0.5)
Orange=(1,0.5,0)
Brown=(0.6,0.5,0.1)
Black=(0,0,0)
White=(1,1,1)
Gray=(0.5,0.5,0.5)

def vtk_show(renderer, width=400, height=300):
    """
    Takes vtkRenderer instance and returns an IPython Image with the rendering.
    """
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetOffScreenRendering(1)
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(width, height)
    renderWindow.Render()
     
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    windowToImageFilter.Update()
     
    writer = vtk.vtkPNGWriter()
    writer.SetWriteToMemory(1)
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()
    data = str(buffer(writer.GetResult()))
    
    return Image(data)

def SetColor(actor,c):
   actor.GetProperty().SetColor(c[0],c[1],c[2])
def SetLineWidth(actor,w):
   actor.GetProperty().SetLineWidth(w)


def MarchingCubes(img_data,isolevel):
    importer = vtk.vtkImageImport()
    img_string = img_data.tostring(order='F')
    dim = img_data.shape
        
    importer.CopyImportVoidPointer(img_string, len(img_string))
    importer.SetDataScalarType(VTK_UNSIGNED_CHAR)
    importer.SetNumberOfScalarComponents(1)
        
    extent = importer.GetDataExtent()
    importer.SetDataExtent(extent[0], extent[0] + dim[0] - 1,
                       extent[2], extent[2] + dim[1] - 1,
                       extent[4], extent[4] + dim[2] - 1)
    importer.SetWholeExtent(extent[0], extent[0] + dim[0] - 1,
                        extent[2], extent[2] + dim[1] - 1,
                        extent[4], extent[4] + dim[2] - 1)
    #importer.SetDataSpacing( dset.pixel_spacing[0], dset.pixel_spacing[1], dset.pixel_spacing[2])
    
    outlineData=vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(importer.GetOutputPort())
    
    mapOutline=vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())
    outline=vtk.vtkActor()
    outline.SetMapper(mapOutline)
    
    skinExtractor=vtk.vtkContourFilter()
    skinExtractor.SetInputConnection(importer.GetOutputPort())
    skinExtractor.SetValue(0,isolevel)
    skinExtractor.Update()
    
    tri=vtk.vtkTriangleFilter()
    tri.SetInputConnection(skinExtractor.GetOutputPort())
    tri.Update()
    
#    deci=vtk.vtkQuadricDecimation()
#    deci.SetInputConnection(tri.GetOutputPort())
#    deci.SetTargetReduction(0.95)
#    # deci-$obj PreserveTopologyOn
#    deci.Update()
    
    skinNormals=vtk.vtkPolyDataNormals()
    #  skinNormals SetInputConnection [skinExtractor GetOutputPort]
    skinNormals.SetInputConnection(tri.GetOutputPort())
    skinNormals.SetFeatureAngle( 60.0)
    
    skinMapper=vtk.vtkPolyDataMapper()
    skinMapper.SetInputConnection(skinNormals.GetOutputPort())
        #  skinMapper SetInputConnection [deci GetOutputPort]
    #skinMapper.ScalarVisibilityOff()
       
    skin=vtk.vtkActor()
    skin.SetMapper(skinMapper)
    return outline,skin

def MakeAxes(point,length):
    xpts=vtk.vtkPoints()
    xlines=vtk.vtkCellArray()
    xpts.InsertNextPoint(point)
    xpts.InsertNextPoint((point[0]+length,point[1],point[2]))
    xlines.InsertNextCell(2)
    xlines.InsertCellPoint(0)
    xlines.InsertCellPoint(1)
    xpoly=vtk.vtkPolyData()
    xpoly.SetPoints(xpts)
    xpoly.SetLines(xlines)

    xpolyMapper=vtk.vtkPolyDataMapper()
    xpolyMapper.SetInputData(xpoly)
       
    xpolyActor=vtk.vtkActor()
    xpolyActor.SetMapper(xpolyMapper)

    SetColor(xpolyActor,Red)
    SetLineWidth(xpolyActor,2)

    ypts=vtk.vtkPoints()
    ylines=vtk.vtkCellArray()
    ypts.InsertNextPoint(point)
    ypts.InsertNextPoint((point[0],point[1]+length,point[2]))
    ylines.InsertNextCell(2)
    ylines.InsertCellPoint(0)
    ylines.InsertCellPoint(1)
    ypoly=vtk.vtkPolyData()
    ypoly.SetPoints(ypts)
    ypoly.SetLines(ylines)

    ypolyMapper=vtk.vtkPolyDataMapper()
    ypolyMapper.SetInputData(ypoly)
       
    ypolyActor=vtk.vtkActor()
    ypolyActor.SetMapper(ypolyMapper)

    SetColor(ypolyActor,Green)
    SetLineWidth(ypolyActor,2)

    zpts=vtk.vtkPoints()
    zlines=vtk.vtkCellArray()
    zpts.InsertNextPoint(point)
    zpts.InsertNextPoint((point[0],point[1],point[2]+length))
    zlines.InsertNextCell(2)
    zlines.InsertCellPoint(0)
    zlines.InsertCellPoint(1)
    zpoly=vtk.vtkPolyData()
    zpoly.SetPoints(zpts)
    zpoly.SetLines(zlines)

    zpolyMapper=vtk.vtkPolyDataMapper()
    zpolyMapper.SetInputData(zpoly)
       
    zpolyActor=vtk.vtkActor()
    zpolyActor.SetMapper(zpolyMapper)

    SetColor(zpolyActor,Blue)
    SetLineWidth(zpolyActor,2)
    return xpolyActor,ypolyActor,zpolyActor


def RenderActors(actors,interactive=True,bgcolor=(1.,1,1)):
	renderer=vtk.vtkRenderer()
	for a in actors:
		renderer.AddActor(a)
	renderer.SetBackground(bgcolor[0],bgcolor[1],bgcolor[2])
 	if interactive:
		renderWindow=vtk.vtkRenderWindow()
		renderWindow.AddRenderer(renderer)
		renderWindow.SetStereoTypeToRedBlue() #Anaglyphic FTW
	 
		renderWindowInteractor=vtk.vtkRenderWindowInteractor()
		renderWindowInteractor.SetRenderWindow(renderWindow)
	 
		renderWindowInteractor.Start()
	
		renderWindow.Finalize()
		renderWindowInteractor.TerminateApp()
		del renderWindow,renderWindowInteractor
        return renderer

def MakePrimalGrid(img_data):
	pts=vtk.vtkPoints()
	lines=vtk.vtkCellArray()
	sz=img_data.shape
	for i in range(sz[0]):
	    for j in range(sz[1]):
	        for k in range(sz[2]):
	            pts.InsertNextPoint((i,j,k))
	for i in range(sz[0]):
	    for j in range(sz[1]):
	        for k in range(sz[2]):
	            if i<sz[0]-1:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2])*(sz[1])+j*(sz[2])+k)
	                lines.InsertCellPoint((i+1)*(sz[2])*(sz[1])+j*(sz[2])+k)
	            if j<sz[1]-1:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2])*(sz[1])+j*(sz[2])+k)
	                lines.InsertCellPoint(i*(sz[2])*(sz[1])+(j+1)*(sz[2])+k)
	            if k<sz[2]-1:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2])*(sz[1])+j*(sz[2])+k)
	                lines.InsertCellPoint(i*(sz[2])*(sz[1])+j*(sz[2])+k+1)
	            
	primal=vtk.vtkPolyData()
	primal.SetPoints(pts)
	primal.SetLines(lines)
	
	scalars=vtk.vtkDoubleArray()
	scalars.SetNumberOfValues(sz[0]*sz[1]*sz[2])
	c=0
	for i in range(sz[0]):
	    for j in range(sz[1]):
	        for k in range(sz[2]):
	            scalars.SetValue(c,(img_data[i,j,k]/255.)*0.2+0.03)
	            c=c+1
	
	
	primal.GetPointData().SetScalars(scalars)
	
	primalMapper=vtk.vtkPolyDataMapper()
	primalMapper.SetInputData(primal)
	primalMapper.ScalarVisibilityOff()
	        #  skinMapper SetInputConnection [deci GetOutputPort]
	    #skinMapper.ScalarVisibilityOff()
	       
	primalActor=vtk.vtkActor()
	primalActor.SetMapper(primalMapper)
	
	primalglyph=vtk.vtkSphereSource()
	primalglyph.SetRadius(0.5)
	primalglyph.SetThetaResolution(12)
	primalglyph.SetPhiResolution(12)
	
	primalPoints=vtk.vtkGlyph3D()
	primalPoints.SetInputData(primal)
	primalPoints.SetSourceConnection(primalglyph.GetOutputPort())
	
	primalPointMapper=vtk.vtkPolyDataMapper()
	primalPointMapper.SetInputConnection(primalPoints.GetOutputPort())
	primalPointMapper.ScalarVisibilityOff()

	primalPointActor=vtk.vtkActor()
	primalPointActor.SetMapper(primalPointMapper)

	return primalActor,primalPointActor

def MakeDualGrid(img_data):
	pts=vtk.vtkPoints()
	lines=vtk.vtkCellArray()
	sz=img_data.shape
	for i in range(sz[0]+1):
	    for j in range(sz[1]+1):
	        for k in range(sz[2]+1):
	            pts.InsertNextPoint((i-0.5,j-0.5,k-0.5))
	for i in range(sz[0]+1):
	    for j in range(sz[1]+1):
	        for k in range(sz[2]+1):
	            if i<sz[0]:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2]+1)*(sz[1]+1)+j*(sz[2]+1)+k)
	                lines.InsertCellPoint((i+1)*(sz[2]+1)*(sz[1]+1)+j*(sz[2]+1)+k)
	            if j<sz[1]:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2]+1)*(sz[1]+1)+j*(sz[2]+1)+k)
	                lines.InsertCellPoint(i*(sz[2]+1)*(sz[1]+1)+(j+1)*(sz[2]+1)+k)
	            if k<sz[2]:
	                lines.InsertNextCell(2)
	                lines.InsertCellPoint(i*(sz[2]+1)*(sz[1]+1)+j*(sz[2]+1)+k)
	                lines.InsertCellPoint(i*(sz[2]+1)*(sz[1]+1)+j*(sz[2]+1)+k+1)
	            
	dual=vtk.vtkPolyData()
	dual.SetPoints(pts)
	dual.SetLines(lines)
	
	dualMapper=vtk.vtkPolyDataMapper()
	dualMapper.SetInputData(dual)
	       
	dualActor=vtk.vtkActor()
	dualActor.SetMapper(dualMapper)
	
	dualglyph=vtk.vtkSphereSource()
	dualglyph.SetRadius(0.03)
	dualglyph.SetThetaResolution(12)
	dualglyph.SetPhiResolution(12)
	
	dualPoints=vtk.vtkGlyph3D()
	dualPoints.SetInputData(dual)
	dualPoints.SetSourceConnection(dualglyph.GetOutputPort())
	
	dualPointMapper=vtk.vtkPolyDataMapper()
	dualPointMapper.SetInputConnection(dualPoints.GetOutputPort())
	
	dualPointActor=vtk.vtkActor()
	dualPointActor.SetMapper(dualPointMapper)
	return dualActor,dualPointActor


def DrawQEFProblem(ax,cs,ps,ns):
	corners=[(0.,0.),(0.,1.),(1.,0.),(1.,1.)]
	A=[]
	b=[]
	for i in range(4):
	    print "i:",ps[i][0]
	    if not np.isnan(ps[i][0]):
	        A.append(ns[i])
	        b.append(np.dot(ns[i],ps[i]))
	A=np.array(A)
	b=np.array(b)
	
	q,res,rank,s=np.linalg.lstsq(A,b.T)
	#print q
	#print "res",res
	#print "rank",rank
	#print "s",s
	#try: 
	#    qq=np.dot(np.linalg.inv(A),b.T)
	#    print qq
	#except:
	#    print "singular"
	def map2axis(pin):
	    return (2+pin[0]*6.,2+pin[1]*6.)
	
	def qef(x,y):
	    q=0.0
	    for i in range(4):
	        if not np.isnan(ps[i][0]):
	           v=(ps[i][0]-x,ps[i][1]-y)
	           nv=ns[i][0]*v[0]+ns[i][1]*v[1]
	           q=q+nv**2
	    return q
	   
	
	        
	# quadratic error functions QEF
	ax.axis("equal")
	ax.set_xlim([0,10])
	ax.set_ylim([0,10])
	
	x,y=np.meshgrid(np.linspace(0,1,20),np.linspace(0,1,20))
	xqef=np.zeros_like(x)
	yqef=np.zeros_like(y)
	zqef=np.zeros_like(x)
	for i in range(x.shape[0]):
	    for j in range(x.shape[1]):
	        xqef[i,j],yqef[i,j]=map2axis((x[i,j],y[i,j]))
	        zqef[i,j]=qef(x[i,j],y[i,j])
	
	
	plt.contour(xqef,yqef,zqef)
	
	
	
	ax.plot([1,9],[2,2],'b-')
	ax.plot([2,2],[1,9],'b-')
	ax.plot([1,9],[8,8],'b-')
	ax.plot([8,8],[1,9],'b-')
	
	z=map2axis(q)
	ax.plot(z[0],z[1],'ro')
	
	for i in range(4):
	    #corners
	    z1=map2axis(corners[i])
	    ax.plot(z1[0],z1[1],'bo',markersize=10) if cs[i]>0 else ax.plot(z1[0],z1[1],marker='o',markersize=10, markerfacecolor='none') 
	    ax.plot([q[0],])
	#points
	    z2=map2axis(ps[i])
	    #ax.plot([z1[0],z2[0]],[z1[1],z2[1]],'k-')
	    ax.plot(z2[0],z2[1],'ko')
	    ax.arrow(z2[0],z2[1],ns[i][0],ns[i][1],head_width=0.25,head_length=0.5,ec='k',fc='k')
	    if not np.isnan(z2[0]):
	        ax.plot([z[0],z2[0]],[z[1],z2[1]],c='silver')
	
	
