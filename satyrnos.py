#!/usr/bin/python

import profile

import ode

import app
import avatar
import drive
import gameobj
import colors
import consenv
import magnet
import joints
import camera
import background
import image
import collision
import sprite
import text
import geommold

from geometry import *
from util import *

app.ui_init()
app.sim_init()

app.objects.append(TrackerList())
app.objects[0].append(gameobj.GameObj(Point(0, -6)))
app.objects[0][0].drives.append(background.DTiledBg("swirlybg.png", Size(100, 100), Size(2, 2), Point(-0.9, -0.9)))
app.objects[0][0].drives.append(background.DTiledBg("hills_dan.png", Size(100, 100), Size(4, 2), Point(-0.7, -0.7), (False, True), Point(0, 5)))

app.objects.append(TrackerList())

app.objects[1].append(gameobj.GameObj(Point(2.5, 0), geom=geommold.BoxGeomMold().make_geom(Size(5, 0.1), app.static_space)))
app.objects[1].append(gameobj.GameObj(Point(0, 5), 0.25, geom=geommold.BoxGeomMold().make_geom(Size(10, 0.1), app.static_space)))
app.objects[1].append(gameobj.GameObj(Point(5, 10), geom=geommold.BoxGeomMold().make_geom(Size(10, 0.1), app.static_space)))
app.objects[1].append(gameobj.GameObj(Point(10, 7.5), 0.25, geom=geommold.BoxGeomMold().make_geom(Size(5, 0.1), app.static_space)))
app.objects[1].append(gameobj.GameObj(Point(7.5, 5), geom=geommold.BoxGeomMold().make_geom(Size(5, 0.1), app.static_space)))
app.objects[1].append(gameobj.GameObj(Point(5, 2.5), 0.25, geom=geommold.BoxGeomMold().make_geom(Size(5, 0.1), app.static_space)))

app.objects[1][0].drives.append(image.DTiledImage("pattern.png", Size(5, 0.1), Size(1, 0.25)))
app.objects[1][1].drives.append(image.DTiledImage("pattern.png", Size(10, 0.1), Size(1, 0.25)))
app.objects[1][2].drives.append(image.DTiledImage("pattern.png", Size(10, 0.1), Size(1, 0.25)))
app.objects[1][3].drives.append(image.DTiledImage("pattern.png", Size(5, 0.1), Size(1, 0.25)))
app.objects[1][4].drives.append(image.DTiledImage("pattern.png", Size(5, 0.1), Size(1, 0.25)))
app.objects[1][5].drives.append(image.DTiledImage("pattern.png", Size(5, 0.1), Size(1, 0.25)))

app.objects[1].append(gameobj.GameObj(
	Point(1, 0.8), 
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(0.75, 0.75), app.static_space),
	drives=[image.DImage("redball.png", Size(0.75, 0.75)), text.DDebugText("Hello nurse", colors.red)]))

app.objects[1].append(gameobj.GameObj(
	Point(1, 2), 0.2,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(1.5, 1.5), app.static_space),
	drives=[image.DImage("redball.png", Size(1.5, 1.5))]))

app.objects[1].append(gameobj.GameObj(
	Point(3.75, 3), 0.7,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(0.75, 0.75), app.static_space),
	drives=[image.DImage("redball.png", Size(0.75, 0.75))]))

app.objects[1].append(gameobj.GameObj(
	Point(1, 3.7), 0.02,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(1.5, 1.5), app.static_space),
	drives=[image.DImage("redball.png", Size(1.5, 1.5))]))

app.objects[1].append(gameobj.GameObj(
	Point(1.5, 5.5), 0.9,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(0.75, 0.75), app.static_space),
	drives=[image.DImage("redball.png", Size(0.75, 0.75))]))

app.objects[1].append(gameobj.GameObj(
	Point(1.7, 7), 0.25,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(1.5, 1.5), app.static_space),
	drives=[image.DImage("redball.png", Size(1.5, 1.5))]))

app.objects[1].append(gameobj.GameObj(
	Point(2.5, 9),
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(0.375, 0.375), app.static_space),
	drives=[image.DImage("redball.png", Size(0.375, 0.375))]))

app.objects[1].append(gameobj.GameObj(
	Point(5.6, 6.7), 0.5,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(1.5, 1.5), app.static_space),
	drives=[image.DImage("redball.png", Size(1.5, 1.5))]))

app.objects[1].append(gameobj.GameObj(
	Point(7.5, 8.7), 0.97,
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(0.75, 0.75), app.static_space),
	drives=[image.DImage("redball.png", Size(0.75, 0.75))]))

app.objects[1].append(gameobj.GameObj(
	Point(8.2, 6.3),
	geom=geommold.CircleGeomMold("redball.png").make_geom(Size(1.5, 1.5), app.static_space),
	drives=[image.DImage("redball.png", Size(1.5, 1.5))]))
	
app.objects.append(TrackerList())

app.objects[2].append(gameobj.GameObj(Point(2.2, 2.5), 0, sphere_body(1, 0.75), geommold.BoxGeomMold().make_geom(Size(1.5, 0.08))))
app.objects[2][0].drives.append(image.DBlock(colors.purple, Size(1.5, 0.08)))
#app.objects[2][0].drives.append(magnet.DRectMagnet(-0.1, Size(1.5, 0.2), loss=0.06))
#app.objects[2][0].drives.append(magnet.DLineMagnet(-0.1, Point(0.75, 0)))
app.objects[2][0].ang = 0.3
app.objects[2][0].drives.append(joints.DEnvJoint(util.anchored_joint(ode.BallJoint, app.objects[2][0])))
app.objects[2][0].drives.append(image.DImage("screw.png", Size(0.1, 0.1), rot_offset = -1))

app.objects[2].append(gameobj.LimbedGameObj(body = sphere_body(1, 0.6)))
app.objects[2][1].geom = geommold.BoxGeomMold().make_geom(Size(0.5, 0.5), app.objects[2][1].space)
app.objects[2][1].pos = Point(4.5, 9)
app.objects[2][1].drives.append(image.DImage("left.png", Size(0.5, 0.5)))
app.objects[2][1].add_limb(gameobj.GameObj(
	Point(4.5, 8.65),
	body=sphere_body(1, 0.375),
	geom=geommold.BoxGeomMold().make_geom(Size(0.2, 0.5), app.objects[2][1].space),
	drives=[image.DBlock(colors.gray, Size(0.2, 0.5))]), Point(0, -0.18))
app.objects[2][1].postdrives.append(image.DImage("screw.png", Size(0.1, 0.1), Point(0, -0.18)))

app.objects[2].append(gameobj.GameObj(
	Point(6, 9.4),
	body=sphere_body(1, 0.4),
	geom=geommold.BoxGeomMold().make_geom(Size(0.5, 0.5)),
	drives=[sprite.DSprite("a",
		{
			"one":image.DImage("1.png", Size(0.5, 0.5)),
			"two":image.DImage("2.png", Size(0.5, 0.5)),
			"three":image.DImage("3.png", Size(0.5, 0.5)),
			"four":image.DImage("4.png", Size(0.5, 0.5))
		}, {
			"a":sprite.DSprite.Anim([("one", 100), ("two", 100), ("three", 100), ("four", 100)], "b"),
			"b":sprite.DSprite.Anim([("four", 700), ("three", 700), ("two", 700), ("one", 700)], "a")
		}
	)]
))

app.objects[2].append(gameobj.GameObj(
	Point(2.5, 1),
	body=sphere_body(0.2, 0.5),
	geom=geommold.CircleGeomMold("ball.png").make_geom(Size(1, 1)),
	drives=[image.DImage("ball.png", Size(1, 1))]))
#app.objects[3][0].drives.append(camera.DCameraLead(bounds=Rect(Point(5, 5), Size(7, 8))))

app.objects.append(TrackerList())

app.objects[3].append(gameobj.GameObj(
	Point(3.3, 4),
	body=sphere_body(0.5, 0.5),
	geom=geommold.CircleGeomMold().make_geom(Size(0.234,0.234)),
	drives=[avatar.DAvatar()]))
app.objects[3][0].drives.append(camera.DCameraDirect())

#app.objects[3].append(gameobj.GameObj(
#	Point(3.3, 5),
#	body=sphere_body(0.5, 0.5),
#	geom=geommold.ComplexGeomMold("pizzaship.png").make_geom(Size(1.0, 1.0), outer = 1, inner = 1),
#	drives=[image.DImage("pizzaship.png", Size(1.0, 1.0))]))
#app.objects[3][0].drives.append(camera.DCameraDirect())

app.objects[3].append(gameobj.GameObj(
	Point(3.3, 5),
	body=sphere_body(0.1, 0.5),
	geom=geommold.CircleGeomMold("ball.png").make_geom(Size(0.1, 0.1)),
	drives=[image.DImage("ball.png", Size(0.1, 0.1))]))

app.objects.append(TrackerList())
app.objects.append(TrackerList())

#app.draw_geoms = True

#profile.run('app.run()', 'satyrprof')
app.run()

app.sim_deinit()
app.ui_deinit()
