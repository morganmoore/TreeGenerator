''' L-System Generator
    
    Implementation:
    The purpose of this program is to create various trees that can be designed to the users specification.
    Attributes such as colour, size, material, and shape will all be adjustable.
    
    The program begins by creating the user interface which contains several user controls.
    Once the apply button is pressed the variables holding the values of the user controls are passed to the treegen function.
    
    In the treegen function the controls are queried using the passed variables and the user interface values are obtained.
    These values can then either be directly passed into the 'creating' functions iterate, createModel and setMaterial
    or used to define variables such as the axiom, rules and material of the tree.
    
    The iterate function uses the basestring (from the chosen treetype/l-system), number of iterations, and the dictionary.
    For each iteration the function replaces each symbol in the basestring with its corresponding value from the dictionary,
    before then assigning the basestring with this newly created 'replaced' string before the next iteration begins.
    
    The primary 'creating' function is createModel which controls the building of the tree and leaves.
    This function uses the ‘finalstring’ generated in the iterate function along with other necessary variables such as length, turn, and leafsize.
    A while loop in the createModel function iterates through the actionstring and checks each symbol against the if/elif cases until a matching case is found, which the program will then enter
    within these if/elif cases the program calls a number of functions to assist with building the tree including createBranch, createVector, makeleaf and makeapple, and also sets new values for variables such as anleX, angleZ and level,
    The cylinders(branches), leaves and apples that are created are then appended to a list which is then used to create groups for each object type that will show up in the outliner of the finished maya scene.
    These groups are then returned to the treegen function where they are then passed (along with colour list, and the material types for the tree and leaves) to the set material function.
    
    In the set material function a set and shading node are created, the user specified colour is then attributed to the shading node and a shader list is created, the material is then assigned to the tree,
    This 'set material' process is repeated for the leaf with its corresponding colour and material attributes from the user, (assuming the leaves checkbox was on)
    The objects have then been set their materials and two tuples (both of two strings) which contain the new shading group name, and the new shader name are returned to the caller
    
    Additional elements of the program include the save undo and cancel tools:
    The undo tool loads the maya file from the previous tree generation
    the save tool creates a window where the user can specify how to save their tree and then save it
    the ‘cancel’ tool calls a the cancelCallback function which closes the main window

  '''  
import maya.cmds as cmds
import math as math
import functools
import ast as ast
import random as rand


def cancelCallback(windowID,*pArgs):
    '''function to close UI window

       windowID		: The identification name of the window
    '''   
    if cmds.window( windowID, exists = True):
        cmds.deleteUI(windowID)

def toggleRadio(leaves, *pArgs):
    '''set leaftype radiogroup to the exact opposite state
    
           leaves		: The path name to the leaves control
        '''   
    #query the value of the leaves radioButtonGrp control
    state =  cmds.radioButtonGrp(leaves, query=True, enable=True)
    
    if state==False:
        cmds.radioButtonGrp( leaves, enable = True, edit = True )        
    elif state==True:
        cmds.radioButtonGrp( leaves, enable = False, edit = True)    
        
def createUI( windowname, pApplyCallback):
    '''Creates the user interface which will recieve various inputs from the user which will later be used to build the tree in the treegen function.
    The user can pick the treetype, the colour of the tree and leaves, the material, the length, the starting angle, the number of iterations, whether they want leaves and apples, 
    the type of leaf, the size of the leaf, and the thickness of the leaves.
    There are also 4 buttons,
    Apply will pass the control path names
    
       windowname	    : the name that will be displayed on the GUI
       pApplyCallback	: the function that the inputs will be passed to when the user clicks apply
    '''
    
    windowID = 'mainwindow'
    
    if cmds.window( windowID, exists=True):
        cmds.deleteUI(windowID)
    cmds.window( windowID, title= windowname , sizeable=False, resizeToFitChildren=True)
    
    cmds.columnLayout( adjustableColumn=True )
    
    #the user interface image that will appear at the top of the window
    submission_path = "/home/s5113911/PythonProgramming"
    cmds.image( w =10, h = 150, i= submission_path+"/Project/panarama4.jpg")
    cmds.separator(h =10, style = 'none')
       
    cmds.text( label ='Tree Type:',align='left')
    
    #controls to choose the treetype
    treetype =cmds.radioButtonGrp( label='', labelArray4=['Standard', 'Dispersed', 'Curved', 'Slant'], numberOfRadioButtons=4, select = 1 )
    treetype2 = cmds.radioButtonGrp( numberOfRadioButtons=2, shareCollection=treetype, label='', labelArray2=['Square', 'Curved2'] )
    
    cmds.separator(h =10, style = 'none')
    
    #control to choose the colour of the tree
    rgbs = cmds.colorSliderGrp( label='Tree Colour:',columnAlign=(1,'left'), rgb=(0.2, 0.08, 0.0) )
    
    cmds.separator(h =10, style = 'none')
    
    #control to choose the colour of the leaves
    rgbleaves = cmds.colorSliderGrp( label='Leaves Colour:',columnAlign=(1,'left'), rgb=(0.06, 0.2, 0.01) )
    
    cmds.separator(h =10, style = 'none')
    cmds.text( label ='Material:',align='left')
    
    #control to choose the material of the tree
    materiall =cmds.radioButtonGrp( label='', labelArray3=['Lambert', 'Blinn', 'Phong'], numberOfRadioButtons=3, select = 1 )
    
    cmds.separator(h =10, style = 'none')
    
    #slider controls to specify the length, angle and iterations of the tree, (iterations meaning th number of the types the chosen l-system will be iterated
    length = cmds.floatSliderGrp(label='Height:', minValue=0.05, maxValue=1.0, value=0.6, step=0.01, field=True, columnAlign=[1,'left'])
    angle = cmds.floatSliderGrp(label='Angle:', minValue=10, maxValue=60, value=25, step=0.01, field=True, columnAlign=[1,'left'])
    iterations = cmds.intSliderGrp( label='Iterations:', minValue=1, maxValue=5, value=4, step=1, field = True, columnAlign=[1,'left'] )
    
    cmds.separator(h =10, style = 'none')
    
    #control to enable or disable apples on the tree
    applecheck = cmds.checkBoxGrp( numberOfCheckBoxes=1, label='Fruit?:  ', columnAlign=[1,'left']  )
    
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    
    cmds.text( label ='Leaf Type:',align='left')
    #control to enable or disable apples on the tree
    leaves =cmds.radioButtonGrp( label='', labelArray2=['Default', 'Maple'], numberOfRadioButtons=2, select = 1, enable = True )
    
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    #control to enable or disable leaves on the tree
    leafcheck = cmds.checkBoxGrp( numberOfCheckBoxes=1, label='Leaves?:  ', columnAlign=[1,'left'], value1 =True, changeCommand1=functools.partial( toggleRadio, leaves )  )
    
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    cmds.text( label ='Leaf Material:',align='left')
    #control to choose the material of the leaves
    materialleaves =cmds.radioButtonGrp( label='', labelArray3=['Lambert', 'Blinn', 'Phong'], numberOfRadioButtons=3, select = 1 )

    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    #control to specify a scaling factor for the leaves
    leafscale = cmds.floatSliderGrp( label='Leafscale:', minValue=0.1, maxValue=3, value=1.2, step=0.01, field = True, columnAlign=[1,'left'])
    
    cmds.separator(h =10, style = 'none')
    cmds.text( label ='Leaves Thickness:',align='left')
    
    #control to specify the 'thickness' of the leaves, e.g if thicker is selected the rule l = ll is added which on average will double the number of leaves created
    leavesamount =cmds.radioButtonGrp( label='', labelArray2=['Default', 'Thicker'], numberOfRadioButtons=2, select = 1)
     
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    
    #creating and defining the flags of the progress bar, which will allow the user to track the programs progress for each tree generation
    progressControl = cmds.progressBar(maxValue=8000, width = 300, bgc =[0.23,0.16,0.0] )
    
    cmds.separator(h =10, style = 'none')
    
    #when the apply button is pressed, the path names of the various controls are passed to the pApplyCallback function( treegen function)
    cmds.button( label='Apply', backgroundColor=[0.9,0.9,0.9], command=functools.partial( pApplyCallback, length, iterations, treetype, materiall, rgbs, leafscale, leavesamount, rgbleaves, applecheck, leafcheck, angle, leaves, treetype2, progressControl, materialleaves) )
             
    cmds.separator(h =10, style = 'none')
    
    #the 'savemenu' fucntion is called
    cmds.button( label = 'Save', command=functools.partial(savemenu), backgroundColor=[0.101,0.338,0.017])
    cmds.separator(h =10, style = 'none') 
    
    #The 'previous' function is called
    cmds.button( label = 'Undo', command=functools.partial(previous), backgroundColor=[0.23,0.16,0.0])
    cmds.separator(h =10, style = 'none')
    
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
    cmds.separator(h =10, style = 'none')
   
    #the cancelCallback function is called
    cmds.button( label = 'Cancel', command=functools.partial( cancelCallback, windowID) )
    
    cmds.separator(h =10, style = 'none')
    
    cmds.showWindow()
    cmds.window(windowID, e=True, width=640)   
    
def savemenu(*pArgs):
    '''creates a window for the user to enter a name and select the format of their generated tree''' 
      
    if cmds.window( 'savemenu', exists=True):
        cmds.deleteUI('savemenu')
    cmds.window( 'savemenu', title= 'Save Menu' , sizeable=False, resizeToFitChildren=True )
    cmds.columnLayout( adjustableColumn=True )
    cmds.text( label='Enter Filename: ',align='left')
    filename = cmds.textField( width=1, text='Filename?')
    fileformats = cmds.radioButtonGrp( numberOfRadioButtons=3, label='File Format:  ', labelArray3=['MayaAscii', 'OBJ', 'MayaBinary'], select = 1)
    
    #when the user clicks the save button the path names of the filename and fileformats controls are passed to the 'save' fucntion
    cmds.button( label='save', backgroundColor=[0.1,0.3,0.2], command=functools.partial( save, fileformats, filename))
    cmds.showWindow() 
       
def save(pfileformat, pfilename, *pArgs):
    '''saves the current file with gthe given format and name
    
       pfileformat	: the user specified file format from savemenu GUI
       pfilename	: the user specified filename from savemenu GUI
    '''
    
    fileformats = []
    filename = cmds.textField(pfilename, query=True, text=True)
    fileformats= cmds.radioButtonGrp(pfileformat, query=True, select=True) 
    
    if fileformats == 1:
        fileformat = "mayaAscii"
    elif fileformats == 2:
        fileformat = "OBJexport"
    elif fileformats == 3:
        fileformat = "mayaBinary"
    else:
        print("Saving was unsuccessful!!!")
    cmds.file(rename="/home/s5113911/PythonProgramming/Project/%s" % filename)
    saved = cmds.file(save=True, type=fileformat)
    print("Saved successfully!!!")
    cancelCallback('savemenu')
    
def previous(*pArgs):
    '''opens the 'previous' file that was saved before the scene was deleted for the current generation, this acts as a simple undo function'''
    
    cmds.file( "/home/s5113911/PythonProgramming/Project/previous.ma", o=True )
    
def addRule(ruleDict, replaceStr, newStr ):
	''' add a new rule to the ruleDict

	ruleDict		: the dictionary holding the rules
	replaceStr		: the old character to be replaced
	newStr			: the new string replacing the old one
	'''
	ruleDict[ replaceStr ] = newStr

def iterate(baseString, numIterations, ruleDict):
	''' following the rules, replace old characters with new ones

	baseString		: start string
	numIterations	: how many times the rules will be used
	ruleDict		: the dictionary holding the rules
	return			: return the final expanded string
	'''
	while numIterations > 0:
		replaced = ""
		for i in baseString:
			replaced = replaced + ruleDict.get(i,i)
		baseString = replaced
		numIterations-=1
	return baseString
	
def createBranch(startPoint, length, angleZ, angleX, level):
	''' create a cylinder for each branch

	startPoint	: startPoint, base point for the new cylinder
	length		: step size for growing
	angleZ		: the 'Z' rotation angle for branching, used for calculating the axis of the cylinder
	angleX		: the 'X' rotation angle for branching, used for calculating the axis of the cylinder
	level       : the number of times the current cyclinder has 'branched off' from the start of the building phase
	return		: return the created object
	'''
	
	radiansZ = angleZ * math.pi /180.0
	radiansX = angleX * math.pi /180.0
	branch = cmds.polyCylinder(axis=[math.sin(radiansZ), math.cos(radiansZ)*math.cos(radiansX), math.cos(radiansZ)*math.sin(radiansX)], r=length/level, height=length)
	
	cmds.move(startPoint[0] + 0.5*length*math.sin(radiansZ), startPoint[1] + 0.5*length*math.cos(radiansZ)*math.cos(radiansX), startPoint[2]+0.5*length*math.cos(radiansZ)*math.sin(radiansX))
	
	return branch[0]

def calculateVector( length, angleZ, angleX ):
	'''calculate the vector from the start point to the end point for each branch

	length		: step size for growing
	rotation	: the rotation angle for branching
	return		: return the vector from start point to end point
	'''
	height = length 
	radiansZ = angleZ * math.pi /180.0
	radiansX = angleX * math.pi /180.0
	return [height* math.sin(radiansZ), height* math.cos(radiansZ)*math.cos(radiansX), height*math.cos(radiansZ)*math.sin(radiansX)]	
	
def makeLeaf(temp, Point):
    '''calculate the vector from the start point to the end point for each branch

	temp		: the product of a random variable rls and the leafscale variable
	Point    	: the current point in the tree generation
	return		: return the name of the created leaf
	'''
    leafy = cmds.duplicate('leafy2')
    rX = rand.uniform(-60,60)
    rY = rand.uniform(0,360)

    cmds.scale( temp, temp, temp, leafy)
    cmds.move(Point[0],Point[1],Point[2],leafy, r = True)

    cmds.rotate(rX,rY,0, leafy, a = True)
    
    return 'leafy*'
        
def makeApple(Point):
    '''calculate the vector from the start point to the end point for each branch

	Point    	: the current point in the tree generation
	return		: return the name of the created apple
	'''
    apple = cmds.duplicate('apple1')

    cmds.scale( 0.1, 0.1, 0.1, apple)
    cmds.move(Point[0],Point[1]-0.8,Point[2],apple)
    return 'apple*'
    
def createModel( actionString, length, turn, leafscale, leaf, apple, progress):
    
   
    '''create the 3D model based on the actionString, following the characters in the string, 
    one by one, grow the branches, and finally group all branches together into one group

      actionString	: instructions on how to construct the model
      length		: step size for growing
      turn			: the rotation angle for branching
      leafscale		: a user selected leaf scaling factor 
      leaf			: a boolean variable set to true when the leaf checkbox is on and false when its off
      apple			: a boolean variable set to true when the apple checkbox is on and false when its off
      progress		: the path name to the progress bar control to allow for editing
      return		: return the group of all the branches, and the leaves and apples (assuming apples and leaves have been selected by the user)
    '''
    
    inputString = actionString
    index = 0		# Where at the input string we start from
    angleX = 0
    angleZ = 0		# Degrees, nor radians
    currentPoint = [0.0, 0.0, 0.0]	# Start from origin
    coordinateStack = []	# Stack where to store coordinates
    angleXStack = []		# Stack to store angles
    angleZStack = []		# Stack to store angles
    branchList = []
    leafList = []
    appleList =[]
    level = 1
    
    #random leaf scaler
    rls = rand.uniform(1.0,1.3)
    temp = leafscale*rls
    
    while ( index < len( inputString ) ):
        if inputString[index] == 'F' or inputString[index] == 'J':
            
            rh = rand.uniform(0.7,1.2)
            branch = createBranch(currentPoint, length, angleZ, angleX, level)
            branchList.append(branch)
            vector = calculateVector( length, angleZ, angleX )
            newPoint = [currentPoint[0] + vector[0], currentPoint[1] + vector[1], currentPoint[2] + vector[2]]
            currentPoint = newPoint	# update the position to go on growing from the new place
            
        elif inputString[index] == 'l' and leaf:
            e= int(rand.uniform(0, level))
            if not e == 0:
                makeLeaf(temp, currentPoint)
                leafList.append('leafy*')       
         
        elif inputString[index] == 'a' and apple:
            e= int(rand.uniform(0, level))
            if  e == 0:
                makeApple(currentPoint)

                appleList.append('apple*')
            
            #cmds.rotate( rand., 0, 0, r=True )
        elif inputString[index] == '-':
            angleZ = angleZ - turn
        elif inputString[index] == '+':
            angleZ = angleZ + turn
        elif inputString[index] == '/':
            angleX = angleX - turn
        elif inputString[index] == '|':
            angleX = angleX + turn
        elif inputString[index] == '[': # add new branches, save the old position into the stack
            coordinateStack.append( currentPoint )
            angleZStack.append( angleZ )
            angleXStack.append( angleX )
            level+=1
            cmds.progressBar(progress, edit=True, step=2)
        elif inputString[index] == ']': # finish the branches, get back to the root position
            currentPoint = coordinateStack.pop()
            angleZ = angleZStack.pop()
            angleX = angleXStack.pop()
            level-=1
        
            #length = length * 0.99
        # Move to the next drawing directive
        index = index + 1
    groupName = cmds.group(branchList, n = "tree")
    
    if apple:
        cmds.group(appleList, n = "apples")
    
        cmds.delete('apple1')
    cmds.progressBar(progress, edit=True, step= 500)
    
    if leaf:
        leavesgroup =cmds.group(leafList, n = "leaves")
        cmds.delete('leafy2')
        
        return groupName, leavesgroup
   
    
    return groupName, "noleaves"
	
def setMaterial(objName, objNameL, materialType, materialTypeL, treecolour, leavescolour, progress):
   '''Assigns a material to the object 'objectName'

      objName      : the group of cylinders making up the trunk and branches of the tree
      objNameL     : the group of leave objects
      materialType : is string that specifies the type of the sufrace shader of the tree(leaves and cyclinders), 
                     this can be any of Maya's valid surface shaders such as:
                     lambert, blin, phong, etc.
      treecolour   : is a list of (R,G,B) values within the range [0,1]
                     which specify the colour of the cyclinders
      leavescolour : is a list of (R,G,B) values within the range [0,1]
                     which specify the colour of the leaves
      progress     : the path name to the progress bar control to allow for editing
      On Exit      : 'objName' and 'objNameL' have been assigned a new material according to the 
                     input values of the procedure, and two tuples (both of two strings) 
                     which contain the new shading group name, and the new shader
                     name are returned to the caller
	'''
   cmds.progressBar(progress, edit=True, pr=8000*0.6)
   
   # create a new set
   setName = cmds.sets(name='_MaterialGroup_', renderable=True, empty=True)
   
   # create a new shading node
   shaderName = cmds.shadingNode(materialType, asShader=True)
   
   # change its colour
   cmds.setAttr(shaderName+'.color', treecolour[0], treecolour[1], treecolour[2], type='double3')
   
   # add to the list of surface shaders
   cmds.surfaceShaderList(shaderName, add=setName)
   
   # assign the material to the object
   cmds.sets(objName, edit=True, forceElement=setName)
   cmds.progressBar(progress, edit=True, pr=8000*0.8)
   
   if not objNameL == "noleaves":
        # create a new set
       setNameL = cmds.sets(name='_MaterialGroup_1', renderable=True, empty=True)
       
       # create a new shading node
       shaderNameL = cmds.shadingNode(materialTypeL, asShader=True)
       
       # change its colour
       cmds.setAttr(shaderNameL+'.color', leavescolour[0], leavescolour[1], leavescolour[2], type='double3')
       
       # add to the list of surface shaders
       cmds.surfaceShaderList(shaderNameL, add=setNameL)
       
       cmds.sets(objNameL, edit=True, forceElement=setNameL)
       
   cmds.progressBar(progress, pr = 8000,  edit=True)
   
def treetype(cv, cv2):
	'''creates the axiom corresponding to the user selected axiom and adds the rules of that axiom '
       cv     : holds the value of the treetype control
       cv2    : holds the value of the treetype2 control
       return : the created axiom and the ruledictionary
       
	'''    

	ruleDictionary = {} # add the rules to the rule dictionary, holding the rules (key, value) such as (F, F + f - FF + F + F F + Ff + FF -f + FF - F - FF - Ff- FFF), (f,ffffff)   
	addRule(ruleDictionary, "F", "FF")
	
	if cv==2:
	    axiom = "A"
	    addRule(ruleDictionary, "A", "FF[+FBl][-FBl][/FBl][|FBl]")
	    addRule(ruleDictionary, "B", "F[/FAla][|FAla]")
	
	elif cv==1:
	    axiom = "C"
	    addRule(ruleDictionary, "C", "F[+|Dl][-/Dl][/Dl][|Dl][Dl]")
	    addRule(ruleDictionary, "D", "FF[+/FCla][-|FCla]")
	        
	elif cv==3:
	    axiom = "G"
	    addRule(ruleDictionary, "G", "F-[[|Gl]+G]+F[+FGla]-G")

	elif cv==4:
	    axiom = "Y"
	    addRule(ruleDictionary, "Y", "F[+FYl][|Yl][-/FY]+F[-FYla]") 
	
	elif cv2==1:
	    axiom = "K"
	    addRule(ruleDictionary, "K", "F[+K][-Kla][/K][|Kla]") 
	        
	else:
	    axiom = "H"
	    addRule(ruleDictionary, "H", "F[+Hl]F[-H]F[/H]F[|Ha][[+Fl]]") 
	       
	return axiom, ruleDictionary
	
	   
def materialtype(cv):
	'''creates the material corresponding to the user selected axiom and adds the rules of that axiom '

      cv     : holds the value of the material control
      return : the string of the selected material
	'''    
	
	if cv == 1:
	    material = "lambert"
	elif cv == 2:
	    material = "blinn"
	else:
	    material = "phong"
	return material
	
def treegen( plength, piterations, ptreetype, pmaterialtype, prgbs, pleafscale, pleavesamount, prgbleaves, papplecheck, pleafcheck, pangle, pleaves, ptreetype2, progress, pleafmaterial, *pArgs):
	'''using the user inputs from createUI to set the variable that will define the characteristics of the tree
	
	  plength       : the path name of the length control which through querying will be used to set the length of the cyclinders that make up the entire tree structure
      piterations   : the path name of the iterations control which through querying will be used to set the number of iterations
      ptreetype     : the path name of the treetype control which through querying will be used to set the axiom and rules for the various treetypes (1-4)
      prgbs         : the path name of the rgbs control which through querying will be used to set the colour of the trunk and branches
      pleavesamount : the path name of the leavesamount control which through querying will be used to set the thickness of the leaves,
                      by specifying the leaf rule (l rule) in the dictionary, e.g l = ll
      prgbleaves    : the path name of the rgbleaves control which through querying will be used to set the rgb of the leaves
      papplecheck   : the path name of the applecheck control which through querying will be used to enable or disable fruit/apples in the tree
      pleafcheck    : the path name of the leafcheck control which through querying will be used to enable or disable leaves in the tree
      pangle        : the path name of the angle control which through querying will be used to set the starting angle in which brnaches in the tree will be created
      pleaves       : the path name of the leaves control which through querying will be used to set the type of leaves that will be generated (maple, standard)
      ptreetype2    : the path name of the treetype2 control which through querying will be used to set the axiom and rules for the 5th 6th and 7th treetypes (5-7)
      progress      : the path name of the progress control which through querying will be used to increment or set the specific value of the progress bar
	   
	'''
	
	cmds.progressBar(progress, pr = 0,  edit=True)
	
	#for the undo tool
	#saving previous scene before it gets deleted for the next tree generation
	cmds.file(rename="/home/s5113911/PythonProgramming/Project/previous")
	saved = cmds.file(save=True, type="mayaAscii")

	# clear up the scene
	cmds.select(all=True)
	cmds.delete()
	
	modelGroup = []
	
	actionString = ""	# the final action string to build the tree
	
	apple = False
	leaf = False
	lamount = 0

	axiom, ruleDictionary = treetype(cmds.radioButtonGrp(ptreetype, query=True, select=True), cmds.radioButtonGrp(ptreetype2, query=True, select=True))
	
	material = materialtype(cmds.radioButtonGrp(pmaterialtype, query=True, select=True))
	leafmaterial = materialtype(cmds.radioButtonGrp(pleafmaterial, query=True, select=True))
	
	leaftype = cmds.radioButtonGrp(pleaves, query=True, select=True)
	
	leavesamount = cmds.radioButtonGrp(pleavesamount, query=True, select=True)
	
	
	if(cmds.checkBoxGrp(papplecheck, query=True, value1=True)):
	    cmds.file("/home/s5113911/PythonProgramming/Project/apple.ma", i=True)
	    #cmds.file("\home\xyang\maya_scripts\submission\models\apple.ma", i = True)
	    apple = True
	    
	if(cmds.checkBoxGrp(pleafcheck, query=True, value1=True)):
	    if leaftype ==1:
	        #cmds.file("/home/s5113911/PythonProgramming/Project/leafy1.ma", i=True)
   	        cmds.file("/home/s5113911/PythonProgramming/Project/leafynomaterial.ma", i=True)
	       
	        #cmds.file("\home\xyang\maya_scripts\submission\models\leafy1.ma", i=True)
	    if leaftype ==2:
	        cmds.file("/home/s5113911/PythonProgramming/Project/mapleleaf2.ma", i=True)
	        #cmds.file("\home\xyang\maya_scripts\submission\models\mapleleaf2.ma", i = True)
	    leaf =True
	   
	iterations = cmds.intSliderGrp(piterations, query=True, value=True)
	stepLength = cmds.floatSliderGrp(plength, query=True, value=True)
	
	rgb = cmds.colorSliderGrp(prgbs, query=True, rgbValue=True)
	leavesrgb = cmds.colorSliderGrp(prgbleaves, query=True, rgbValue=True)
	leafscale = cmds.floatSliderGrp(pleafscale, query=True, value=True)
	angle = cmds.floatSliderGrp(pangle, query=True, value=True)
	
   
	if leavesamount==2:
	    addRule(ruleDictionary, "l", "ll")
	    lamount = 2
	
	# create the action string
	finalString=iterate(axiom, iterations, ruleDictionary)
	
	# create the 3D model
	modelGroup = createModel(finalString, stepLength, angle, leafscale, leaf, apple, progress)
	
	
	# set the color to green
	setMaterial(modelGroup[0], modelGroup[1], material, leafmaterial, rgb ,leavesrgb, progress)
	
	
# main program, start with the function buildTree()
if __name__ == "__main__":
	createUI('TreeGen', treegen)