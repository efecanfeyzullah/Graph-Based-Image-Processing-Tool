from PIL import Image
import copy
import base64
import io

# User class
class User:
    def __init__(self, name):
        self.name = name

# Component base class
class Component:
    def __init__(self, name, inports, outports):
        self.name = name
        self.inports = inports      # Example: [("Input", "image"), ("Width", "int"), ("Height", "int")]
        self.outports = outports    # Example: [("Output", "image"), ("Something", "int")]
        self.isInteractive = False

    def execute(self, inp):
        pass

    def skip_execute(self, nodedata):
        pass

### Derived component classes

# Interactive components
class LoadImage(Component):
    def execute(self, inp):
        #img_name = input("LoadImage input: ")
        img_name = inp[0]
        with open(img_name, 'rb') as f:
            img_bytes = f.read()
        img_str = base64.b64encode(img_bytes).decode()
        return [img_str]
    
    def skip_execute(self, nodedata):
        img_str = nodedata["value"]
        img_bytes = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_bytes))
        # img.show()
        return [img]
class GetString(Component):
    def execute(self, inp):
        #string = input("GetString input: ")
        string = inp[0]
        return [string]
class GetInteger(Component):
    def execute(self, inp):
        #val = int(input("GetInteger input: "))
        val = int(inp[0])
        return [val]
    def skip_execute(self, nodedata):
        val = nodedata["value"]
        intval = int(val)
        #print ("intval-> " + str(intval) + "  -- " + str(type(intval)))
        return [intval]

class GetFloat(Component):
    def execute(self, inp):
        #val = float(input("GetFloat input: "))
        val = float(inp[0])
        return [val]
    def skip_execute(self, nodedata):
        val = nodedata["value"]
        floatval = float(val)
        #print ("floatval-> " + str(floatval) + "  -- " + str(type(floatval)))
        return [floatval]
# Editing Components
class RotateImage(Component):
    def execute(self, inp):
        image = inp[0]
        image = image.rotate(inp[1])
        return [image]
class ScaleImage(Component):
    def execute(self, inp):
        image = inp[0]
        w, h = image.size
        w = w * inp[1]
        h = h * inp[1]
        w, h = int(w), int(h)
        image = image.resize((w, h))
        return [image]
class CropImage(Component):
    def execute(self, inp):
        image = inp[0]
        image = image.crop((inp[1], inp[2], inp[3], inp[4]))  # left, top, right, bottom
        return [image]
class FitImage(Component):
    def execute(self, inp):
        image = inp[0]
        image = image.resize((inp[1], inp[2]))
        return [image]
class StretchImage(Component):
    def execute(self, inp):
        image = inp[0]
        image = image.resize((inp[1], inp[2]))
        return [image]
class StackImage(Component):
    def execute(self, inp):
        image1 = inp[0]
        image2 = inp[1]
        w1, h1 = image1.size
        w2, h2 = image2.size
        combinedImage = Image.new(mode="RGB", size=(max(w1, w2), h1 + h2))
        combinedImage.paste(image1, (0, 0, w1, h1))
        combinedImage.paste(image2, (0, h1, w2, h2 + h1))
        return [combinedImage]
class HStackImage(Component):
    def execute(self, inp):
        image1 = inp[0]
        image2 = inp[1]
        w1, h1 = image1.size
        w2, h2 = image2.size
        combinedImage = Image.new(mode="RGB", size=(w1 + w2, max(h1, h2)))
        combinedImage.paste(image1, (0, 0, w1, h1))
        combinedImage.paste(image2, (w1, 0, w1 + w2, h2))
        return [combinedImage]

# Other Components
class SaveImage(Component):
    # input -> newImageName
    def execute(self, inp):
        image = inp[0]
        imageName = inp[1]
        image.save(imageName)
class DupImage(Component):
    def execute(self, inp):
        image = inp[0]
        return [image, copy.deepcopy(image)]
class GetDimensions(Component):
    def execute(self, inp):
        image = inp[0]
        w, h = image.size
        return [(w, h)]
class ViewImage(Component):
    def execute(self, inp):
        image = inp[0]
        image.show()
        return []

# Node class for graph
class Node:
    availableID = 0         # Available id, next object will get this id
    def __init__(self, componenttype, id):
        if id == -1:
            self.id = Node.availableID
        else:
            self.id = id
        Node.availableID += 1   # Increment availableID, next node will get the new available id

        self.inportValues = []
        self.outportValues = []

        self.componenttype = componenttype
        self.component = Component("default", [], [])
        # Create a component depending on the component type
        if componenttype == "LoadImage":
            self.component = LoadImage("LoadImage", [("ImageName", "string")], [("Output", "Image")])
            self.component.isInteractive = True
        elif componenttype == "GetString":
            self.component = GetString("GetString", [("ConnectedTo", "string")], [("EnteredValue", "string")])
            self.component.isInteractive = True
        elif componenttype == "GetInteger":
            self.component = GetInteger("GetInteger", [("ConnectedTo", "string")], [("EnteredValue", "int")])
            self.component.isInteractive = True
        elif componenttype == "GetFloat":
            self.component = GetFloat("GetFloat", [("ConnectedTo", "string")], [("EnteredValue", "float")])
            self.component.isInteractive = True
            
        elif componenttype == "RotateImage":
            self.component = RotateImage("RotateImage", [("Input", "Image"), ("Angle", "float")], [("Output", "Image")])
        elif componenttype == "ScaleImage":
            self.component = ScaleImage("ScaleImage", [("Input", "Image"), ("ScaleFactor", "float")], [("Output", "Image")])
        elif componenttype == "CropImage":
            self.component = CropImage("CropImage", [("Input", "Image"), ("Left", "int"), ("Top", "int"), ("Right", "int"), ("Bottom", "int")], [("Output", "Image")])
        elif componenttype == "FitImage":
            self.component = FitImage("FitImage", [("Input", "Image"), ("Width", "int"), ("Height", "int")], [("Output", "Image")])
        elif componenttype == "StretchImage":
            self.component = StretchImage("StretchImage", [("Input", "Image"), ("Width", "int"), ("Height", "int")], [("Output", "Image")])
        elif componenttype == "StackImage":
            self.component = StackImage("StackImage", [("Input 1", "Image"), ("Input 2", "Image")], [("Output", "Image")])
        elif componenttype == "HStackImage":
            self.component = HStackImage("HStackImage", [("Input 1", "Image"), ("Input 2", "Image")], [("Output", "Image")])

        elif componenttype == "SaveImage":
            self.component = SaveImage("SaveImage", [("Input", "Image"), ("ImageName", "string")], [("Output", "file")])
            self.component.isInteractive = True
        elif componenttype == "DupImage":
            self.component = DupImage("DupImage", [("Input", "Image")], [("Duplicate", "file"), ("Duplicate", "file")])
        elif componenttype == "GetDimensions":
            self.component = GetDimensions("GetDimensions", [("Input", "Image")], [("Width", "int"), ("Height", "int")])
        elif componenttype == "ViewImage":
            self.component = ViewImage("ViewImage", [("Input", "Image")], [])

        # All ports are initialized to None
        for inport in self.component.inports:
            self.inportValues.append(None)
        for outport in self.component.outports:
            self.outportValues.append(None)

    def execute(self):
        outport = self.component.execute(self.inportValues)
        self.outportValues = outport
        return self.outportValues
    
    def set_outport(self, nodedata):
        outport = self.component.skip_execute(nodedata)
        self.outportValues = outport
        return outport
        

# Core graph class
class Graph:
    def __init__(self, name, user):
        self.name = name
        self.user = user
        self.nodes = dict()     # Can get nodes using their ids, dictionary will look like this -> { 0: node0, 1: node1, 2: node2 }
        self.connections = []   # Sample connection tuple: (id of the outport holder node, outport name, id of the inport holder node, inport name)
        self.componenttypesstr = ""
        self.componenttypesstr += "LoadImage: it is an interactive component, asking user for an input with \"file\" type and outputs an \"image\" type.\n"
        self.componenttypesstr += "GetString: it inputs a string from user and provides output in \"str\" type.\n"
        self.componenttypesstr += "GetInteger: it inputs an integer from user and provides output in \"int\" type.\n"
        self.componenttypesstr += "GetFloat: it inputs a floating point number from user and provides output in \"float\" type.\n"
        self.componenttypesstr += "Crop: Crop a rectangular area in the image and return the new image.\n"
        self.componenttypesstr += "GetDimensions: it inputs an image and returns two integers for dimensions.\n"
        self.componenttypesstr += "Rotate: Gets an image and a float and returns a new image.\n"
        self.componenttypesstr += "Stack: Gets two images and tile them one on top of other to form a new image.\n"
        self.componenttypesstr += "HStack: Gets two images and tile them adjacent to each other.\n"
        self.componenttypesstr += "Scale: Gets an image and a float value, scales image with given value.\n"
        self.componenttypesstr += "Fit: Gets an image and scales them to fit in a box defined in the input dimensions.\n"
        self.componenttypesstr += "Stretch: Gets an image and scale it by stretching both dimensions in the given box.\n"
        self.componenttypesstr += "SaveImage: save image into user supplied \"file\".\n"
        self.componenttypesstr += "ViewImage: open an image viewer to show the image.\n"
        self.componenttypesstr += "DupImage: Inputs an image and outputs the same image as two images so that it can be chained to two different nodes/components."

    def newnode(self, componenttype, id = -1):
        node = Node(componenttype, id)
        self.nodes[node.id] = node
        return node

    def connect(self, node1, outport, node2, inport):
        self.connections.append((node1, outport, node2, inport))    # node1 and node2 are node ids, outport and inport are port names

    def disconnect(self, node1, outport, node2, inport):
        self.nodes[node1].outportValues[outport] = None
        self.nodes[node2].inportValues[inport] = None
        self.connections.remove((node1, outport, node2, inport))    # node1 and node2 are node ids, outport and inport are port names

    def updateConnections(self):
        for connection in self.connections:
            # node0Id, n0OutportId, node1Id, n1InportId
            # 0      , 1          , 2      , 3
            node0 = self.nodes[connection[0]]
            node1 = self.nodes[connection[2]]
            node1.inportValues[connection[3]] = node0.outportValues[connection[1]]

    def isvalid(self):
        for node in self.nodes.values():    # Go over all nodes and check if any inport is disconnected
            if node.component.isInteractive:    # Skip interactive components
                continue
            i = 0
            while i < len(node.inportValues):
                inportConnected = False
                for connection in self.connections:
                    if connection[2] == node.id and connection[3] == i:
                        inportConnected = True
                if not inportConnected:
                    return False
                i += 1
        return True        

    def runparams(self):
        result = []
        nodeList = self.nodes.values()
        for node in nodeList:
            connectedInportIds = []
            for connection in self.connections:
                if connection[2] == node.id:
                    connectedInportIds.append(connection[3])
            inportCount = len(node.component.inports)
            for inportId in range(inportCount):
                if connectedInportIds.find(inportId) == -1:
                    result.append(node.component.inports[inportId])
        return result


    def execute(self, params):
        if self.isvalid():  # Execute if valid
            print("Validation complete.")
            # Execute all nodes
            nodeList = self.nodes.values()
            output = None
            for node in nodeList:
                if not node.component.isInteractive:
                    output = node.execute()
                self.updateConnections()
            print("Execution complete.")
            # Add all disconnected outport values to a tuple and return it
            # allOutportValues = []
            # for node in nodeList:
            #     for value in node.outportValues:
            #         if value == None:
            #             allOutportValues.append(value)
            # allOutportValues = tuple(allOutportValues)
            # return allOutportValues
            return output[0]
        else:
            print("Validation failed.")
            return None

    def getcomponenttypes(self):
        # LoadImage: it is an interactive component, asking user for an input with "file" type and outputs an "image" type.
        # GetInteger: it inputs an integer from user and provides output in "int" type.
        # GetFloat: it inputs a floating point number from user and provides output in "float" type.
        # Crop: Crop a rectangular area in the image and return the new image.
        # GetDimensions: it inputs an image and returns two integers for dimensions.
        # Rotate: Gets an image and a float and returns a new image.
        # Stack: Gets two images and tile them one on top of other to form a new image.
        # HStack: Gets two images and tile them adjacent to each other.
        # Scale: Gets an image and a float value, scales image with given value.
        # Fit: Gets an image and scales them to fit in a box defined in the input dimensions.
        # Stretch: Gets an image and scale it by stretching both dimensions in the given box.
        # SaveImage: save image into user supplied "file"
        # ViewImage: open an image viewer to show the image.
        # DupImage: Inputs an image and outputs the same image as two images so that it can be chained to two different nodes/components.   
        return self.componenttypesstr
    
    def setWithDict(self, gDict):
        self.name = gDict["name"]
        self.user = User(gDict["user"])

        nodeIDs = list(gDict["nodes"].keys())
        nodeDicts = list(gDict["nodes"].values())
        i = 0
        while i < len(nodeIDs):
            self.nodes[int(nodeIDs[i])] = Node(nodeDicts[i]["componenttype"], int(nodeIDs[i]))
            self.nodes[int(nodeIDs[i])].inportValues = nodeDicts[i]["inportValues"]
            self.nodes[int(nodeIDs[i])].outportValues = nodeDicts[i]["outportValues"]
            i += 1

        Node.availableID = gDict["nodeAvailableID"]

        self.connections = gDict["connections"]
        self.componenttypesstr = gDict["componenttypesstr"]

    def getDict(self):
        result = {}

        result["name"] = self.name
        result["user"] = self.user.name
        
        result["nodeAvailableID"] = Node.availableID
        result["nodes"] = {}

        nodesKeyList = list(self.nodes.keys())
        nodesValueList = list(self.nodes.values())
        i = 0
        while i < len(nodesKeyList):
            result["nodes"][nodesKeyList[i]] = {}
            result["nodes"][nodesKeyList[i]]["id"] = nodesValueList[i].id
            result["nodes"][nodesKeyList[i]]["inportValues"] = nodesValueList[i].inportValues
            result["nodes"][nodesKeyList[i]]["outportValues"] = nodesValueList[i].outportValues
            result["nodes"][nodesKeyList[i]]["componenttype"] = nodesValueList[i].componenttype
            i += 1

        result["connections"] = self.connections
        result["componenttypesstr"] = self.componenttypesstr

        return result
