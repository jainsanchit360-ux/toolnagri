from build import build_tool_page

def register():
    # ---------------- Image Compressor (pure canvas, no external lib needed) ----------------
    panel = """
    <div id="ic-dropzone" class="drop-zone">
      <p><strong>Drag & drop an image here</strong>, or</p>
      <label class="btn btn-secondary" for="ic-file" style="display:inline-flex;margin-top:6px">Choose image</label>
      <input id="ic-file" type="file" accept="image/jpeg,image/png,image/webp" style="display:none">
      <p class="search-hint">JPG, PNG or WEBP, up to 15 MB. Processed entirely in your browser &mdash; never uploaded.</p>
    </div>
    <div id="ic-controls" style="display:none;margin-top:18px">
      <div class="field">
        <label for="ic-quality">Quality: <span id="ic-quality-val">70</span>%</label>
        <input id="ic-quality" type="range" min="10" max="95" value="70">
      </div>
      <div class="result-grid">
        <div class="item"><div class="label">Original size</div><div class="val" id="ic-orig-size">-</div></div>
        <div class="item"><div class="label">Compressed size</div><div class="val" id="ic-new-size">-</div></div>
        <div class="item"><div class="label">Reduction</div><div class="val" id="ic-reduction">-</div></div>
      </div>
      <div class="row-actions" style="margin-top:14px">
        <a id="ic-download" class="btn btn-primary" download="compressed-image.jpg">Download compressed image</a>
        <button type="button" id="ic-reset" class="btn btn-secondary">Choose another image</button>
      </div>
    </div>
    <div id="error-box" class="error-msg hidden"></div>
    """
    script = """
    (function(){
      var dz = document.getElementById('ic-dropzone');
      var fileInput = document.getElementById('ic-file');
      var controls = document.getElementById('ic-controls');
      var qualityInput = document.getElementById('ic-quality');
      var img = new Image();
      var origSize = 0;
      function showError(msg){
        var box = document.getElementById('error-box');
        box.textContent = msg; box.classList.remove('hidden');
      }
      ['dragover','dragenter'].forEach(function(evt){
        dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.add('dragover'); });
      });
      ['dragleave','drop'].forEach(function(evt){
        dz.addEventListener(evt, function(e){ e.preventDefault(); dz.classList.remove('dragover'); });
      });
      dz.addEventListener('drop', function(e){
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
      });
      fileInput.addEventListener('change', function(){
        if (fileInput.files.length) handleFile(fileInput.files[0]);
      });
      function handleFile(file){
        document.getElementById('error-box').classList.add('hidden');
        if (!/^image\\/(jpeg|png|webp)$/.test(file.type)) { showError('Please choose a JPG, PNG or WEBP image.'); return; }
        if (file.size > 15*1024*1024) { showError('File is too large. Please choose an image under 15 MB.'); return; }
        origSize = file.size;
        var reader = new FileReader();
        reader.onload = function(e){
          img.onload = function(){ controls.style.display='block'; compress(); };
          img.onerror = function(){ showError('Could not read this image. Please try a different file.'); };
          img.src = e.target.result;
        };
        reader.onerror = function(){ showError('Could not read this file.'); };
        reader.readAsDataURL(file);
      }
      function compress(){
        var canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth; canvas.height = img.naturalHeight;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        var quality = parseInt(qualityInput.value, 10) / 100;
        document.getElementById('ic-quality-val').textContent = qualityInput.value;
        var dataUrl = canvas.toDataURL('image/jpeg', quality);
        var byteLength = Math.round((dataUrl.length - dataUrl.indexOf(',') - 1) * 3/4);
        document.getElementById('ic-orig-size').textContent = formatBytes(origSize);
        document.getElementById('ic-new-size').textContent = formatBytes(byteLength);
        var reduction = origSize > 0 ? Math.max(0, (1 - byteLength/origSize)*100) : 0;
        document.getElementById('ic-reduction').textContent = reduction.toFixed(0) + '%';
        var dl = document.getElementById('ic-download');
        dl.href = dataUrl;
      }
      function formatBytes(b){
        if (b < 1024) return b + ' B';
        if (b < 1024*1024) return (b/1024).toFixed(1) + ' KB';
        return (b/1024/1024).toFixed(2) + ' MB';
      }
      qualityInput.addEventListener('input', compress);
      document.getElementById('ic-reset').addEventListener('click', function(){
        controls.style.display = 'none';
        fileInput.value = '';
      });
    })();
    """
    build_tool_page(
        "image-compressor", panel, script,
        how_it_works="<p>Your image is drawn onto an in-memory HTML canvas and re-encoded as JPEG at the quality level you choose, using your browser's built-in image encoder. Lower quality means a smaller file at the cost of some visual detail. The file never leaves your device.</p>",
        example="<p>A 4 MB PNG photo compressed at 70% quality typically becomes a 300&ndash;800 KB JPEG, depending on image content, with minimal visible quality loss for web/sharing use.</p>",
        faqs=[
            ("Is my image uploaded to a server?", "No. Compression happens entirely in your browser using the Canvas API. The image is never sent over the network."),
            ("Why can't I hit an exact target file size?", "Compression quality (10&ndash;95%) controls the trade-off between file size and visual quality, but the exact resulting size depends on image content, so we don't promise a specific guaranteed size."),
        ],
    )

    # ---------------- QR Code Generator (uses CDN qrcode.js) ----------------
    panel = """
    <form id="qr-form">
      <div class="field">
        <label for="qr-type">QR type</label>
        <select id="qr-type">
          <option value="text">Text / URL</option>
          <option value="phone">Phone number</option>
          <option value="email">Email</option>
          <option value="wifi">Wi-Fi</option>
        </select>
      </div>
      <div id="qr-fields"></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Generate QR Code</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden" style="text-align:center">
      <div id="qr-canvas-wrap"></div>
      <div class="row-actions" style="justify-content:center;margin-top:14px">
        <a id="qr-download" class="btn btn-secondary" download="qrcode.png">Download PNG</a>
      </div>
    </div>
    """
    script = """
    (function(){
      var typeSel = document.getElementById('qr-type');
      var fieldsEl = document.getElementById('qr-fields');
      var TEMPLATES = {
        text: '<div class="field"><label for="q1">Text or URL</label><textarea id="q1" placeholder="https://example.com"></textarea></div>',
        phone: '<div class="field"><label for="q1">Phone number (with country code)</label><input id="q1" type="text" placeholder="+919876543210"></div>',
        email: '<div class="field"><label for="q1">Email address</label><input id="q1" type="text" placeholder="name@example.com"></div><div class="field"><label for="q2">Subject (optional)</label><input id="q2" type="text"></div>',
        wifi: '<div class="field"><label for="q1">Network name (SSID)</label><input id="q1" type="text"></div><div class="field"><label for="q2">Password</label><input id="q2" type="text"></div><div class="field"><label for="q3">Security</label><select id="q3"><option value="WPA">WPA/WPA2</option><option value="WEP">WEP</option><option value="nopass">None</option></select></div>'
      };
      function render(){ fieldsEl.innerHTML = TEMPLATES[typeSel.value]; }
      typeSel.addEventListener('change', render);
      render();
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('qr-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        if (typeof QRCode === 'undefined') { showError('The QR code library failed to load. Please check your internet connection and try again.'); return; }
        var type = typeSel.value, payload = '';
        var q1 = document.getElementById('q1') ? document.getElementById('q1').value.trim() : '';
        if (!q1) { showError('Please fill in the required field.'); return; }
        if (type === 'text') payload = q1;
        else if (type === 'phone') payload = 'tel:' + q1.replace(/\\s+/g,'');
        else if (type === 'email') {
          var subject = document.getElementById('q2') ? document.getElementById('q2').value.trim() : '';
          payload = 'mailto:' + q1 + (subject ? '?subject=' + encodeURIComponent(subject) : '');
        } else if (type === 'wifi') {
          var pass = document.getElementById('q2').value.trim();
          var sec = document.getElementById('q3').value;
          payload = 'WIFI:T:' + sec + ';S:' + q1 + ';P:' + pass + ';;';
        }
        var wrap = document.getElementById('qr-canvas-wrap');
        wrap.innerHTML = '';
        new QRCode(wrap, { text: payload, width: 220, height: 220 });
        setTimeout(function(){
          var canvas = wrap.querySelector('canvas');
          var img = wrap.querySelector('img');
          var dataUrl = canvas ? canvas.toDataURL('image/png') : (img ? img.src : null);
          if (dataUrl) document.getElementById('qr-download').href = dataUrl;
        }, 100);
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('qr-form').reset();
        render();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "qr-code-generator", panel, script,
        how_it_works="<p>We encode your text, link, phone number, email or Wi-Fi details into a QR code image directly in your browser using an open-source QR encoding library. Nothing you enter is sent to a server.</p>",
        example="<p>Entering a URL generates a scannable QR code that opens that link when scanned with any phone camera. Wi-Fi QR codes let guests join your network without typing the password.</p>",
        faqs=[
            ("Do QR codes expire?", "No, the QR codes generated here encode your data directly (not a redirect link), so they don't expire or depend on our servers staying online."),
            ("Is my Wi-Fi password safe?", "The QR code is generated locally in your browser and never uploaded, but remember that anyone who scans the resulting QR code image will be able to see/use your Wi-Fi password."),
        ],
        extra_head='<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>',
    )
