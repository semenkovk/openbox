#ifndef __render_h
#define __render_h

#include <X11/Xlib.h>
#define _XFT_NO_COMPAT_ /* no Xft 1 API */
#include <X11/Xft/Xft.h>
#include <glib.h>
#include "color.h"

#ifdef HAVE_STDINT_H
#  include <stdint.h>
#else
#  ifdef HAVE_SYS_TYPES_H
#    include <sys/types.h>
#  endif
#endif

#ifdef HAVE_STDINT_H
typedef uint32_t pixel32;
typedef uint16_t pixel16;
#else
typedef u_int32_t pixel32;
typedef u_int16_t pixel16;
#endif /* HAVE_STDINT_H */

#if (G_ENDIAN == G_BIG_ENDIAN)
#define default_red_shift 0
#define default_green_shift 8
#define default_blue_shift 16
#define endian MSBFirst
#else
#define default_red_shift 16
#define default_green_shift 8
#define default_blue_shift 0
#define endian LSBFirst
#endif /* G_ENDIAN == G_BIG_ENDIAN */

typedef enum {
    Surface_Planar,
    Surface_Nonplanar
} SurfaceType;

typedef enum {
    Flat,
    Raised,
    Sunken
} ReliefType;

typedef enum {
    Bevel1,
    Bevel2
} BevelType;

typedef enum {
    Background_ParentRelative,
    Background_Solid,
    Background_Horizontal,
    Background_Vertical,
    Background_Diagonal,
    Background_CrossDiagonal,
    Background_PipeCross,
    Background_Rectangle,
    Background_Pyramid,
    Background_Elliptic
} SurfaceColorType;

typedef enum {
    Bitmask,
    Text,
    RGBA
} TextureType;

typedef struct PlanarSurface {
    SurfaceColorType grad;
    ReliefType relief;
    BevelType bevel;
    color_rgb *primary;
    color_rgb *secondary;
    color_rgb *border_color;
    gboolean interlaced;
    gboolean border;
    pixel32 *pixel_data;
} PlanarSurface;

typedef struct NonplanarSurface {
    int poo;
} NonplanarSurface;

typedef union {
    PlanarSurface planar;
    NonplanarSurface nonplanar;
} SurfaceData;

typedef struct Surface {
    SurfaceType type;
    SurfaceColorType colortype;
    SurfaceData data;
} Surface;

typedef struct {
    XftFont *xftfont;
} ObFont;

typedef struct TextureText {
    ObFont *font;
    int shadow;  
    unsigned char tint;
    unsigned char offset;
    color_rgb *color;
    char *string;
} TextureText;   

typedef struct {
    Pixmap mask;
    guint w, h;
} pixmap_mask;

typedef struct TextureMask {
    color_rgb *color;
    pixmap_mask *mask;
} TextureMask;

typedef struct TextureRGBA {
    int poo;
} TextureRGBA;

typedef union {
    TextureRGBA rgba;
    TextureText text;
    TextureMask mask;
} TextureData;

typedef struct Texture {
    TextureType type;
    TextureData data;
} Texture;

typedef struct Appearance {
    Surface surface;
    int textures;
    Texture *texture;
    Pixmap pixmap;
    XftDraw *xftdraw;
} Appearance;

extern Visual *render_visual;
extern int render_depth;
extern Colormap render_colormap;

void (*paint)(Window win, Appearance *l, int w, int h);

void render_startup(void);
void init_appearance(Appearance *l);
void x_paint(Window win, Appearance *l, int w, int h);
void render_shutdown(void);
Appearance *appearance_new(SurfaceType type, int numtex);
Appearance *appearance_copy(Appearance *a);
void appearance_free(Appearance *a);
#endif /*__render_h*/
