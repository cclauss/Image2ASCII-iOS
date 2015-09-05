#Run this file

import console, dialogs, _dialogs, io, photos, time, ui
from PIL import Image
from Image2ASCII import image2ASCII, RenderASCII

class ShadowView(ui.View):
    '''A class for a ui.View that has a shadow behind it.

    This is accomplished by:
    1. Draw the background
    2. Redraw with a shadow, but set clipping so only the edge of the shadow
    shows. This prevents the part of the shadow that's under the background
    from showing.

    '''
    def draw(self):
        '1'
        #Setup path of window shape
        path = ui.Path.rect(0, 0, self.width - 10, self.height - 10)

        #Draw background
        ui.set_color((0.95, 0.95, 0.95, 0.5))
        path.fill()

        '2'
        #Setup mask by creating image
        from PIL import ImageDraw
        img = Image.new('RGBA', (520,290), (255,255,255,0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((self.width-10, 0, self.width, self.height), fill=(0,0,0,255))
        draw.rectangle((0, self.height-10, self.width, self.height), fill=(0,0,0,255))

        #Convert to UI, apply the mask, and draw shadow!
        img = pil_to_ui(img)
        img.clip_to_mask()
        ui.set_color((1,1,1,1))
        ui.set_shadow("black",-2,-2,10)
        path.fill()


def pil_to_ui(img):
    with io.BytesIO() as b:
        img.save(b, "PNG")
        return ui.Image.from_data(b.getvalue())

@ui.in_background
def image_take(sender):
    im = photos.capture_image()
    if im:
        rootView.remove_subview(view1)
        main(im)

@ui.in_background
def image_pick(sender):
    im = photos.pick_image()
    if im:
        main(im)
        rootView.remove_subview(view1)

def seg_action(sender):
    if sc.selected_index == 0:
        view2.add_subview(tshare)
        view2.remove_subview(ishare)
    elif sc.selected_index == 1:
        view2.add_subview(ishare)
        view2.remove_subview(tshare)

def pull_down():
    view2.y = 0

@ui.in_background
def export_text(sender):
    dialogs.share_text(out)

@ui.in_background
def export_image(sender):
    console.show_activity()
    ishare['colorbox'].end_editing()
    color = ishare['colorbox'].text
    if color:
        if not color.startswith('#'):
            color = '#'+color
        if len(color) != 7:
            raise ValueError('Must be hexidecimal')
        im = RenderASCII(out, bgcolor=color)
        image_view.image = pil_to_ui(im)
        rootView.background_color = color
        view2.draw()
    else:
        im = outim
    with io.BytesIO() as b:
        im.save(b, 'PNG')
        img_data = b.getvalue()
    console.hide_activity()
    _dialogs.share_image_data(img_data)

def main(im):
    global out, outim, image_view
    out = image2ASCII(im)
    outim = RenderASCII(out)
    rootView.background_color = 0.92
    image_view = ui.ImageView()
    image_view.frame = (0, 10, 1024, 768)
    image_view.content_mode = ui.CONTENT_SCALE_ASPECT_FIT
    image_view.image = pil_to_ui(outim)
    rootView.add_subview(image_view)

    view2.remove_subview(ishare)
    view2.x = 247
    view2.y = -285
    rootView.add_subview(view2)

    time.sleep(1.5)
    ui.animate(pull_down, 1)

rootView = ui.View(frame=(0, 0, 1024, 768))
view1 = ui.load_view()

#Build view2
view2 = ui.load_view('Popup.pyui')
view2.background_color = (0.93,0.93,0.93,0.0)

ishare = view2['ShareImage']
ishare['colorbox'].autocapitalization_type = ui.AUTOCAPITALIZE_NONE
tshare = view2['ShareText']

sc = view2['segcon']
sc.action = seg_action

rootView.add_subview(view1)
rootView.present('full_screen', hide_title_bar=True)
