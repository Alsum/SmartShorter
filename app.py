# app.py

import argparse
import string

import random
import simplejson
from flask import Flask, make_response, jsonify, request
from models import Shortlink, Ios, Android
from mongoframes import *
from pymongo import MongoClient


def create_app(env):
    """
    We use an application factory to allow the app to be configured from the
    command line at start up.
    """

    # Create the app
    app = Flask(__name__)

    # Configure the application to the specified config
    app.config['ENV'] = env
    app.config.from_object('settings.{0}.Config'.format(env))

    # Set up MongoFrames
    app.mongo = MongoClient(app.config['MONGO_URI'])
    Frame._client = app.mongo
    db = app.mongo
    if app.config.get('MONGO_PASSWORD'):
        Frame.get_db().authenticate(
                app.config.get('MONGO_USERNAME'),
                app.config.get('MONGO_PASSWORD')
        )

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'status': 'failed', 'message': 'Not found'}), 404)

    @app.errorhandler(400)
    def bad_request(error):
        return make_response(jsonify({'status': 'failed', 'message': 'Bad Request'}), 400)

    @app.errorhandler(500)
    def special_exception_handler(error):
        return make_response(jsonify({}), 500)

    @app.route('/shortlinks', methods=['GET'])
    def get_shortlinks():
        # return simplejson.dumps(Shortlink.many(projection={'ios': {'$sub': Ios}, 'android': {'$sub': Android}}),for_json=True)
        shortlinks = db.mydb.Shortlink.find()
        output = []
        for q in shortlinks:
            output.append({'slug': q['slug'], 'ios': q['Ios'], 'android': q['Android'], 'web': q['web']})
        return jsonify({'shortlinks': output})

    @app.route('/shortlinks', methods=['POST'])
    def add_shortlink():

        ios_primary = request.json['ios']['primary']
        ios_fallback = request.json['ios']['fallback']
        android_primary = request.json['android']['primary']
        android_fallback = request.json['android']['fallback']
        web = request.json['web']

        if 'slug' not in request.json.keys():
            slug = ''.join(random.sample(string.ascii_lowercase, 10, ))
        else:
            slug = request.json['slug']

        ios_p_base = ios_primary.rsplit('/', 1)[0]
        ios_primary = ios_p_base + '/' + slug
        ios_f_base = ios_fallback.rsplit('/', 1)[0]
        ios_fallback = ios_f_base + '/' + slug
        android_p_base = android_primary.rsplit('/', 1)[0]
        android_primary = android_p_base + '/' + slug
        android_f_base = android_fallback.rsplit('/', 1)[0]
        android_fallback = android_f_base + '/' + slug
        web_base = web.rsplit('/', 1)[0]
        web = web_base + '/' + slug

        shortlink = Shortlink(
                slug=slug,
                Ios=[Ios(primary=ios_primary, fallback=ios_fallback)],
                Android=[Android(primary=android_primary, fallback=android_fallback)],
                web=web,
        )

        shortlink.insert()
        return make_response(jsonify({'status': 'successful', "slug": slug, 'message': 'created successfully'}), 201)

    @app.route('/shortlinks/<slug>', methods=['PUT'])
    def update_shortlink(slug):

        for key, value in request.json.items():

            if key == 'web':
                db.mydb.Shortlink.update(
                        {"slug": slug},
                        {
                            "$set": {key: value},
                        }
                )
            if hasattr(value, 'keys'):

                if 'fallback' in value.keys():
                    db.mydb.Shortlink.update(
                            {"slug": slug},
                            {
                                "$set": {key.capitalize() + ".0.fallback": value['fallback']
                                         },
                            }
                    )

                if 'primary' in value.keys():
                    db.mydb.Shortlink.update(
                            {"slug": slug},
                            {
                                "$set": {key.capitalize() + ".0.primary": value['primary']
                                         },
                            }
                    )

        return make_response(jsonify({'status': 'successful', 'message': 'updated successfully'}), 201)

    return app


if __name__ == "__main__":
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='Application server')
    parser.add_argument(
            '-e',
            '--env',
            choices=['dev', 'local', 'prod'],
            default='local',
            dest='env',
            required=False
    )
    args = parser.parse_args()

    # Create and run the application
    app = create_app(args.env)
    app.run(port=app.config.get('PORT'))
