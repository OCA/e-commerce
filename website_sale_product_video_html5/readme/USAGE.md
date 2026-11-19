1.  Open a product, and add a media in *eCommerce Media* of the
    *Sales* tab.
2.  Fill in the *Video URL* with the URL of the video file, e.g.
    `https://cdn.example.com/videos/product.mp4`.
3.  Upload an image: it is used as thumbnail in the product page carousel and
    as poster of the video.

The player can be tuned by adding parameters to the video URL:

- `autoplay=1`: start playing on page load, muted (browsers block autoplay
  with sound);
- `loop=1`: play the video in a loop;
- `controls=0`: hide the player controls.

These parameters are removed from the URL the browser loads, so signed CDN
URLs keep working.

As the computation only depends on the URL, video media can also be created
by imports or through the API.
