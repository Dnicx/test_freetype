#!/usr/bin/env python3
import sys
import sdl2
from OpenGL import GL
import ctypes

import os

import freetype

FontFilePath = 'C:\\Users\\theer\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Roboto-Regular.ttf'

# Vertex shader source code
vertex_shader_source = """
#version 330 core
layout (location = 0) in vec3 a_position;
void main()
{
    gl_Position = vec4(a_position, 1.0);
}
"""

# Fragment shader source code
fragment_shader_source = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 1.0, 1.0, 1.0);  // White color
}
"""

# Vertex data for a simple triangle
vertices = [
    -0.5, -0.5, 0.0,
    0.5, -0.5, 0.0,
    0.0, 0.5, 0.0
]

def compile_shader(shader_source, shader_type):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, shader_source)
    GL.glCompileShader(shader)
    
    # Check compilation status
    if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
        info_log = GL.glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compilation failed: {info_log}")
    
    return shader

def handleEvent( event ):
    print( event )

    match event.type:
        case sdl2.SDL_KeyboardEvent:
            print( f'key event {event.key}')
        
        case sdl2.SDL_QUIT:
            sys.exit( 0 )

def initFontFace( fontPath, size_px ):

        
    print(f'path exist {os.path.exists( fontPath )}')
    face = freetype.Face( fontPath )
    face.set_pixel_sizes( 0, size_px )

    return face


def render_text( face, text ):

    # Set up a bitmap
    face.load_char( text[0], freetype.FT_LOAD_FLAGS['FT_LOAD_RENDER'])
    bitmap = face.glyph.bitmap

    # Create texture
    texture_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RED, bitmap.width, bitmap.rows, 0, GL.GL_RED, GL.GL_UNSIGNED_BYTE, bitmap.buffer)

    # Set texture parameters
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)

    # Draw textured quad
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord2f(0, 1)
    GL.glVertex2f(0, 0)
    GL.glTexCoord2f(1, 1)
    GL.glVertex2f(1, 0)
    GL.glTexCoord2f(1, 0)
    GL.glVertex2f(1, 1)
    GL.glTexCoord2f(0, 0)
    GL.glVertex2f(0, 1)
    GL.glEnd()
    GL.glDisable(GL.GL_TEXTURE_2D)

    # Clean up texture
    GL.glDeleteTextures(1, [texture_id])

def main():
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print(f"SDL initialization failed: {sdl2.SDL_GetError()}")
        return -1
    
    # Create SDL window
    window = sdl2.SDL_CreateWindow(b"OpenGL Playground", 
                                    sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
                                    800, 600, 
                                    sdl2.SDL_WINDOW_OPENGL)
    if not window:
        print(f"Failed to create SDL window: {sdl2.SDL_GetError()}")
        sdl2.SDL_Quit()
        return -1
    
    # Create OpenGL context
    gl_context = sdl2.SDL_GL_CreateContext(window)
    
    # Initialize OpenGL
    if not gl_context:
        print(f"Failed to create OpenGL context: {sdl2.SDL_GetError()}")
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()
        return -1
    
    # Compile shaders
    vertex_shader = compile_shader(vertex_shader_source, GL.GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL.GL_FRAGMENT_SHADER)
    
    # Create shader program
    shader_program = GL.glCreateProgram()
    GL.glAttachShader(shader_program, vertex_shader)
    GL.glAttachShader(shader_program, fragment_shader)
    GL.glLinkProgram(shader_program)
    
    # Check linking status
    if not GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS):
        info_log = GL.glGetProgramInfoLog(shader_program).decode()
        raise RuntimeError(f"Shader program linking failed: {info_log}")
    
    # Create and bind vertex array object (VAO)
    vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vao)
    
    # Create vertex buffer object (VBO)
    vbo = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    
    # Copy vertex data to VBO
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(GL.GLfloat) * len(vertices), (GL.GLfloat * len(vertices))(*vertices), GL.GL_STATIC_DRAW)
    
    # Specify vertex attribute pointer
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * ctypes.sizeof(GL.GLfloat), None)
    GL.glEnableVertexAttribArray(0)

    font = initFontFace( FontFilePath, 30*64 )
    
    # Main loop
    running = True
    while running:
        # Process events
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent( ctypes.byref( event ) ):
            handleEvent( event )

            if event.type == sdl2.SDL_QUIT:
                return

        
        # Clear the screen
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        
        # # Use shader program
        # GL.glUseProgram(shader_program)
        
        # # Draw the triangle
        # GL.glBindVertexArray(vao)
        # GL.glDrawArrays(GL.GL_TRIANGLES, 0, len(vertices) // 3)

        render_text( font, 'test'.encode())
        
        # Swap buffers
        sdl2.SDL_GL_SwapWindow(window)
    
    # Cleanup
    GL.glDeleteProgram(shader_program)
    GL.glDeleteShader(vertex_shader)
    GL.glDeleteShader(fragment_shader)
    GL.glDeleteBuffers(1, [vbo])
    GL.glDeleteVertexArrays(1, [vao])
    
    sdl2.SDL_GL.GL_DeleteContext(GL.gl_context)
    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

    return 0

if __name__ == "__main__":
    sys.exit(main())
