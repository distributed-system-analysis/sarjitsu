'use strict';

// Gruntfile.js
module.exports = function(grunt) {

  require('logfile-grunt')(grunt);

  // Load grunt tasks automatically, when needed
  require('jit-grunt')(grunt, {
    express: 'grunt-express-server'
  });

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  grunt.initConfig({
    // Project settings
    pkg: grunt.file.readJSON('package.json'),

    express: {
      options: {
        port: process.env.PORT || 1337
      },
      dev: {
        options: {
          script: 'server.js',
          debug: true
        }
      },
      prod: {
        options: {
          script: 'server.js'
        }
      }
    },

    env: {
      test: {
        NODE_ENV: 'test'
      },
      prod: {
        NODE_ENV: 'production'
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            'safiles/', 'sessions/'
          ]
        }]
      },
      server: ['safiles/', 'sessions/']
    },

    // Debugging with node inspector
    'node-inspector': {
      custom: {
        options: {
          'web-host': 'localhost'
        }
      }
    },

    // configure nodemon
    nodemon: {
      dev: {
        script: 'server.js',
        env: {
          PORT: 1337
        },
        options: {
          ignore: ["safiles/*"]
        }
      },
      debug: {
        script: 'server.js',
        options: {
          nodeArgs: ['--debug-brk'],
          env: {
            PORT: process.env.PORT || 1337
          },
          callback: function(nodemon) {
            nodemon.on('log', function(event) {
              console.log(event.colour);
            });
          }
        }
      }
    },

    watch: {
      gruntfile: {
        files: ['Gruntfile.js', 'scripts/*', 'server.js']
      },
      livereload: {
        files: [
          'static/*.json',
          'static/**/**/.js',
          'static/**/**/.css',
        ],
        options: {
          livereload: true
        }
      },
      express: {
        files: [
          'static/**/*.{js,json}',
          'static/*.{js,json}'
        ],
        tasks: ['express:dev', 'wait'],
        options: {
          livereload: true,
          nospawn: true //Without this option specified express won't be reloaded
        }
      }
    },

    concurrent: {
      debug: {
        tasks: [
          'nodemon',
          'node-inspector'
        ],
        options: {
          logConcurrentOutput: true
        }
      }
    },

  });

  // Used for delaying livereload until after server has restarted
  grunt.registerTask('wait', function() {
    grunt.log.ok('Waiting for server reload...');

    var done = this.async();

    setTimeout(function() {
      grunt.log.writeln('Done waiting!');
      done();
    }, 1500);
  });

  grunt.registerTask('express-keepalive', 'Keep grunt running', function() {
    this.async();
  });

  grunt.registerTask('build', [
    'clean:dist',
    'concat',
    'copy:dist',
    'cssmin',
    'uglify',
  ]);

  grunt.registerTask('serve', function(target) {
    if (target === 'dist') {
      return grunt.task.run(['build', 'env:prod', 'express:prod', 'wait', 'express-keepalive']); // 'open',
    }

    if (target === 'debug') {
      return grunt.task.run([
        'clean:server',
        'concurrent:debug'
      ]);
    }

    grunt.task.run([
      'clean:server',
      'express:dev',
      'wait',
      'watch'
    ]);
  });
  
  grunt.registerTask('server', function() {
    grunt.log.warn('The `server` task has been deprecated. Use `grunt serve` to start a server.');
    grunt.task.run(['serve']);
  });

  // register the nodemon task when we run grunt
  grunt.registerTask('default', ['nodemon']);  

};
