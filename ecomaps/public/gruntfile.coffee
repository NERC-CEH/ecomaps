module.exports = (grunt) ->
  grunt.initConfig
    bowerDirectory: require('bower').config.directory

    less:
      compile:
        options:
          compress: false
          paths: ['less', 'tmp', '<%= bowerDirectory %>/bootstrap/less']
        files:
          'css/bootstrap.css': ['less/theme.less']

    recess:
      dist:
        options:
          compile: true
        files:
          'css/bootstrap.css': ['css/bootstrap.css']

    watch:
      less:
        files: ['less/*.less']
        tasks: ['copy', 'less:compile', 'clean']
      cssmin:
        files: ['css/bootstrap.css']
        tasks: ['cssmin:minify']
        options:
          livereload: true

    cssmin:
      minify:
        expand: true
        cwd: 'css'
        src: ['bootstrap.css']
        dest: 'css'
        ext: '.min.css'

    connect:
      serve:
        options:
          port: grunt.option('port') || '9000'
          hostname: grunt.option('host') || 'localhost'

    copy:
      bootstrap:
        files: [
          { expand: true, cwd: '<%= bowerDirectory %>/bootstrap/less', src: ['bootstrap.less'], dest: 'tmp/' },
          { expand: true, cwd: '<%= bowerDirectory %>/bootstrap/fonts', src: ['*'], dest: 'fonts' },
          { expand: true, cwd: '<%= bowerDirectory %>/bootstrap/dist/js', src: ['bootstrap.min.js'], dest: 'js' }
        ]
      jquery:
        files: [
          { expand: true, cwd: '<%= bowerDirectory %>/jquery/dist', src: ['*'], dest: 'js' }
        ]

    clean: ['tmp']

  grunt.loadNpmTasks('grunt-contrib-less')
  grunt.loadNpmTasks('grunt-recess')
  grunt.loadNpmTasks('grunt-contrib-watch')
  grunt.loadNpmTasks('grunt-contrib-cssmin')
  grunt.loadNpmTasks('grunt-contrib-copy')
  grunt.loadNpmTasks('grunt-text-replace')
  grunt.loadNpmTasks('grunt-contrib-clean')
  grunt.loadNpmTasks('grunt-contrib-connect')

  grunt.registerTask('default', ['copy', 'less', 'recess', 'cssmin', 'clean'])
  grunt.registerTask('serve', ['connect', 'watch'])