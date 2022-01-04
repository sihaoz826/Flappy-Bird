#################################################
# flappy bird.py
#
# Your name: Sihao Zhou
# Your andrew id: sihaoz
#################################################

import math, copy, random
from cmu_112_graphics import *


class Pipe(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

#################################################
# Helper functions
#################################################

# https://www.cs.cmu.edu/~112/notes/notes-data-and-operations.html
def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

# draws the image size
# https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#loadImageUsingFile
def drawImageWithSizeBelowIt(app, canvas, image, cx, cy):
    canvas.create_image(cx, cy, image=ImageTk.PhotoImage(image))
    imageWidth, imageHeight = image.size
    msg = f'Image size: {imageWidth} x {imageHeight}'
    canvas.create_text(cx, cy + imageHeight/2 + 20,
                       text=msg, font='Arial 20 bold')

# move the bird down
def moveBirdDown(app):
    app.birdY += app.gravity * app.birdControl**2

# move the bird up
def moveBirdUp(app):
    app.birdY -= 20
    resetGravityControl(app)

# move the bird left
def moveBirdLeft(app):
    app.birdX -= 5

# move the bird right
def moveBirdRight(app):
    app.birdX += 5

# move the ground
def moveGround(app):
    app.groundX -= 5
    if app.groundX == 100:
        app.groundX = 150

# create a new pipe
def createPipe(app):
    # generate a random midpoint if the difference between up and low is less 
    # than 1, and the number of up and low midpoints are recorded in app.midDic
    # upup = (125, 187)
    # up = (188, 250)
    # low = (251, 312)
    # lowlow = (313, 375)
    if abs(app.midDic['upup'] + app.midDic['up'] 
        - app.midDic['low'] - app.midDic['lowlow']) <= 1:
        newMid = random.randint(125, 375)
        # if belongs to up, append it to up
        if 125 <= newMid <= 187:
            app.midDic['upup'] += 1
        elif 188 <= newMid <= 250:
            app.midDic['up'] += 1
        elif 251 <= newMid <= 312:
            app.midDic['low'] += 1
        else:
            app.midDic['lowlow'] += 1
    else:
    # when the upper half has more midpoints than the lower half
        if (app.midDic['upup'] + app.midDic['up']) >\
            (app.midDic['low'] + app.midDic['lowlow']):
            if app.midDic['low'] == app.midDic['lowlow']:
                newMid = random.randint(251, 375)
                if 251 <= newMid <= 312:
                    app.midDic['low'] += 1
                else:
                    app.midDic['lowlow'] += 1
            elif app.midDic['low'] > app.midDic['lowlow']:
                newMid = random.randint(313, 375)
                app.midDic['lowlow'] += 1
            elif app.midDic['low'] < app.midDic['lowlow']:
                newMid = random.randint(251, 312)
                app.midDic['low'] += 1
        
        # when the lower half has more midpoints than the upper half
        elif (app.midDic['upup'] + app.midDic['up']) <\
            (app.midDic['low'] + app.midDic['lowlow']):
            if app.midDic['upup'] == app.midDic['up']:
                newMid = random.randint(125, 250)
                if 125 <= newMid <= 187:
                    app.midDic['upup'] += 1
                else:
                    app.midDic['up'] += 1
            elif app.midDic['upup'] > app.midDic['up']:
                newMid = random.randint(188, 250)
                app.midDic['up'] += 1
            elif app.midDic['upup'] < app.midDic['up']:
                newMid = random.randint(125, 187)
                app.midDic['upup'] += 1


    # the passage way through the pipes is gonna be a random number
    passageLen = passageLength(app)

    # pipe paramters
    pipeW = 52
    pipeH = 320

    # down pipe
    downX = 340
    downY = newMid - passageLen/2 - pipeH/2
    newDownPipe = Pipe(downX, downY)
    app.downPipeList.append(newDownPipe)

    # up pipe
    upX = 340
    upY = newMid + passageLen/2 + pipeH/2
    newUpPipe = Pipe(upX, upY)
    app.upPipeList.append(newUpPipe)

# make the passage length between pipes smaller and smaller
# the rate of decrease is becoming bigger and bigger 
def passageLength(app):
    start = 200
    length = start - app.passageControl**2
    if length <= 130:
        length = 130
    return length

# makes the distance between pipes going smaller and smaller
# connected with timerFired
def pipeDistance(app):
    result = 70
    if 0 < app.pipeTimePassed <= 400:
        result = 70
    elif 400 < app.pipeTimePassed <= 700:
        result = 60
    elif 700 < app.pipeTimePassed <= 1000:
        result = 50
    elif 1000 < app.pipeTimePassed <= 1300:
        result = 40
    elif 1300 < app.pipeTimePassed <= 1600:
        result = 30
    else:
        result = 20
    return result

# move the pipes
def movePipes(app):
    move = app.timePassed * 0.01 + 5
    if move >= 15:
        move = 15
    for pipe in app.downPipeList:
        pipe.x -= move
    for pipe in app.upPipeList:
        pipe.x -= move

# check if two rectangles overlap
def rectanglesOverlap(x1, y1, w1, h1, x2, y2, w2, h2):
    if (x2 > x1 and y2 < y1 and y1 - y2 <= h2 and x2 - x1 <= w1):
        return True
    elif (x2 > x1 and y1 < y2 and y2 - y1 <= h1 and x2 - x1 <= w1):
        return True
    elif (x2 < x1 and y2 < y1 and y1 - y2 <= h2 and x1 - x2 <= w2):
        return True
    elif (x2 < x1 and y1 < y2 and y2 - y1 <= h1 and x1 - x2 <= w2):
        return True
    else:
        return False

# check collision
def checkCollision(app):
    # bird 
    bHor = 48/2
    bVer = 35/2
    birdx0 = app.birdX - bHor
    birdy0 = app.birdY - bVer
    birdx1 = app.birdX + bHor
    birdy1 = app.birdY + bVer

    # height of the ground
    groundH = app.groundY - (73/2)

    # collides with ceiling
    if birdy0 <= 0:
        return True
    # collides with ground 
    elif birdy1 >= groundH:
        return True

    # bird stuff
    birdW = 45
    birdH = 32
    birdX = app.birdX - (birdW/2)
    birdY = app.birdY - (birdH/2)

    adj = 0
    # up pipes 
    for pipe in app.upPipeList:
        upX = pipe.x - 26
        upY = pipe.y - 160
        upW = 26 * 2
        upH = 160 * 2
        if rectanglesOverlap(upX, upY, upW, upH, birdX, birdY, birdW, birdH):
            return True
    
    # down pipes around
    for pipe in app.downPipeList:
        downX = pipe.x - 26
        downY = pipe.y - 160
        downW = 26 * 2
        downH = 160 * 2 
        if rectanglesOverlap(downX, downY, downW, downH, 
                            birdX, birdY, birdW, birdH):
            return True

    # check collision for the pig
    # pig stuff
    w1 = 40
    h1 = 38
    x1 = app.pigX - (w1/2)
    y1 = app.pigY - (h1/2)

    if rectanglesOverlap(x1, y1, w1, h1, birdX, birdY, birdW, birdH):
        return True

    # check collision for the enemy bird
    # enemy bird stuff
    eBirdW = 40
    eBirdH = 42
    eBirdX = app.enemyBirdX - (eBirdW/2)
    eBirdY = app.enemyBirdY - (eBirdH/2)

    if rectanglesOverlap(eBirdX, eBirdY, eBirdW, eBirdH,
                        birdX, birdY, birdW, birdH):
        return True
    
    # if none of the above is true, return false
    return False

# increase the score on top of screen
def increaseScore(app):
    if app.upPipeList != []:
        bHor = 48/2
        birdx0 = app.birdX - bHor

        lastPipe = app.upPipeList[-1]
        upx0 = lastPipe.x - 26
        upx1 = lastPipe.x + 26
        
        app.score = len(app.upPipeList)

            
# the pig moves in a projectile motion
def movePig(app):
    # desired apex on the canvas
    canvasApex = 250
    # actual input in function
    functionApex = (app.height * 13/14) - canvasApex
    # use app.pigX to determine height of the pig
    ctr = app.pigX
    tempY = (-functionApex/10000)*(ctr**2) + (functionApex/25)*ctr -\
             (functionApex*3)
    app.pigY = (app.height * 13/14) - tempY
    # make it repetitive
    if app.pigX >= 300:
        app.pigX = 100

# return the distance between two points
def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**0.5

# the enemy bird is always chasing the block in front of and below the bird
def moveEnemyBird(app):
    app.targetX = app.birdX + app.width/2
    app.targetY = app.birdY + 200

    ctr = 2
    # going right
    rightX = app.enemyBirdX + ctr
    rightY = app.enemyBirdY
    # going down
    downX = app.enemyBirdX
    downY = app.enemyBirdY + ctr
    # going up 
    upX = app.enemyBirdX
    upY = app.enemyBirdY - ctr
    # distances
    right = distance(rightX, rightY, app.targetX, app.targetY)
    down = distance(downX, downY, app.targetX, app.targetY)
    up = distance(upX, upY, app.targetX, app.targetY)
    minDis = min(right, down, up)
    # set the move according to the minimum distance
    if minDis == right:
        app.enemyBirdX = rightX
        app.enemyBirdY = rightY
    elif minDis == down:
        app.enemyBirdX = downX
        app.enemyBirdY = downY
    else:
        app.enemyBirdX = upX
        app.enemyBirdY = upY
    # reset the enemy bird after it reaches close to the block right of the brid
    if distance(app.enemyBirdX, app.enemyBirdY, app.targetX, app.targetY) < 20:
        app.enemyBirdX = 0
        app.enemyBirdY = 0


#################################################
# Model
#################################################
def appStarted(app):
    reset(app)

def reset(app):
    # starting parameters
    app.isGameOver = False
    app.notStarted = True
    app.paused = False
    app.timerDelay = 20
    app.timePassed = 1
    app.score = 0


    # controls the movement of the flappy bird
    resetGravityControl(app)

    # dimensions
    width = 340
    height = 580 

    # background
    app.background = app.loadImage('background_2.png')
    app.background = app.scaleImage(app.background, 4/3)
    app.backgroundX = width/2
    app.backgroundY = height/2

    # bird
    s1 = app.loadImage('bird.png')
    s2 = app.loadImage('bird2.png')
    app.bird = [s1, s2]
    app.spriteCounter = 0
    # bird location
    app.birdX = width/2
    app.birdY = height/2


    # ground
    app.ground = app.loadImage('ground.png')
    app.groundX = width/2
    app.groundY = height*14/15
    
    # pipe lists
    app.downPipeList = []
    app.upPipeList = []

    # mid point dictionary to keep track of the pipes location and optimization
    app.midDic = {'upup':0, 'up':0, 'low':0, 'lowlow': 0}

    # down pipe
    app.downPipe = app.loadImage('pipe-down.png')

    # up pipe
    app.upPipe = app.loadImage('pipe-up.png')

    # game over
    app.picGameOver = app.loadImage('gameover.png')

    # pig
    app.pig = app.loadImage('pig.png')
    app.pig = app.scaleImage(app.pig, 2/5)
    app.pigX = 100
    app.pigY = app.height * 13/14

    # enemy bird
    app.enemyBird = app.loadImage('enemy bird.png')
    app.enemyBird = app.scaleImage(app.enemyBird, 1/5)
    app.enemyBirdX = app.width * 0/2
    app.enemyBirdY = app.height * 0/2

    # target
    app.targetX = app.birdX + app.width/2
    app.targetY = app.birdY + 200

    # passage
    app.passageControl = 0.01

    # pipe time passed
    app.pipeTimePassed = 20

    # pipe distance
    app.pipeDistance = 60


def resetGravityControl(app):
    app.gravity = 0.7
    app.birdControl = 0.15

#################################################
# Controller
#################################################

def keyPressed(app, event):
    # moves the bird down
    if event.key == 'Up':
        moveBirdUp(app)
    # moves the bird up
    elif event.key == 'Down':
        app.birdY += 20
    # moves the bird left
    elif event.key == 'Left':
        moveBirdLeft(app)
    # moves the bird right
    elif event.key == 'Right':
        moveBirdRight(app)
    # starts the game/ pause
    elif event.key == 's':
        app.notStarted = not app.notStarted
    # pause the game
    elif event.key == 'p':
        app.paused = not app.paused
    # resets the game
    elif event.key == 'r':
        reset(app)

def mousePressed(app, event):
    moveBirdUp(app)

def timerFired(app):
    # starting the game
    if app.notStarted == True:
        return
    # pause the game
    if app.paused == True:
        return 
    # constantly checking collition
    if checkCollision(app) == True:
        app.isGameOver = True
    # if game over, no movements
    if app.isGameOver == True:
        return 

    # moves the flappy bird
    app.birdControl += 0.15

    # time passed used to create pipes and increase score
    app.pipeTimePassed += 1
    result = pipeDistance(app)
    if almostEqual(app.pipeTimePassed % result, 0):
        createPipe(app)
        increaseScore(app)
    
    # spriteCounter for animating the bird
    app.timePassed += 1
    if app.timePassed % 4 == 0:
        app.spriteCounter = (1 + app.spriteCounter) % len(app.bird)

    # using app.pigX to move the pig
    app.pigX += 1
    movePig(app)

    # passage control
    app.passageControl += 0.01

    # move the enemy bird
    moveEnemyBird(app)

    moveBirdDown(app)
    moveGround(app)
    movePipes(app)



#################################################
# View
#################################################

def redrawAll(app, canvas):

    drawBackGround(app, canvas)   
    drawDownPipe(app, canvas)
    drawUpPipe(app, canvas)
    drawBird(app, canvas)
    drawPig(app, canvas)
    drawEnemyBird(app, canvas)
    drawGround(app, canvas)
    drawScore(app, canvas)
    if app.notStarted == True:
        drawGuide(app, canvas)
    if app.isGameOver == True:
        drawGameOver(app, canvas)

def drawGuide(app, canvas):
    canvas.create_text(app.width/2, app.height*4/10,
                        text = 'Hello!!!',
                        font = 'Arial 30 bold',
                        fill = 'white')
    canvas.create_text(app.width/2, app.height*6/10,
                        text = 'Press s to start the game!',
                        font = 'Arial 20 bold',
                        fill = 'white') 

def drawBackGround(app, canvas):
    canvas.create_image(app.backgroundX, app.backgroundY,
                        image=ImageTk.PhotoImage(app.background))

def drawBird(app, canvas):
    sprite = app.bird[app.spriteCounter]
    canvas.create_image(app.birdX, app.birdY,
                        image=ImageTk.PhotoImage(sprite))

def drawGround(app, canvas):
    canvas.create_image(app.groundX, app.groundY,
                        image=ImageTk.PhotoImage(app.ground))

def drawDownPipe(app, canvas):
    for pipe in app.downPipeList:
        x = pipe.x
        y = pipe.y
        canvas.create_image(x, y,
                            image=ImageTk.PhotoImage(app.downPipe))

def drawUpPipe(app, canvas):
    for pipe in app.upPipeList:
        x = pipe.x
        y = pipe.y
        canvas.create_image(x, y,
                            image=ImageTk.PhotoImage(app.upPipe))

def drawScore(app, canvas):
    canvas.create_text(app.width/2, 0,
                        fill = 'white',
                        text = f'{app.score}',
                        font = 'Arial 40 bold',
                        anchor = 'n')

def drawGameOver(app, canvas):
    canvas.create_text(app.width/2, app.height*4/10,
                        text = 'Game Over!!!',
                        font = 'Arial 30 bold',
                        fill = 'white')
    canvas.create_text(app.width/2, app.height*5/10,
                        text = 'Press r to restart!',
                        font = 'Arial 20 bold',
                        fill = 'white')                    

def drawPig(app, canvas):
    canvas.create_image(app.pigX, app.pigY,
                            image=ImageTk.PhotoImage(app.pig))

def drawEnemyBird(app, canvas):
    canvas.create_image(app.enemyBirdX, app.enemyBirdY,
                        image=ImageTk.PhotoImage(app.enemyBird))

#################################################
# Runner
#################################################
def playFlappy():
    runApp(width = int(340), height = int(580))

playFlappy()