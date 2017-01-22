#!/bin/sh

git push
git push heroku master

heroku ps:scale clock=1
heroku open
