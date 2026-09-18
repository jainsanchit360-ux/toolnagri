from build import build_tool_page

def register():
    # ---------------- Resume Builder ----------------
    panel = """
    <form id="rb-form">
      <h3 style="margin-top:0">Personal information</h3>
      <div class="subject-row" style="grid-template-columns:1fr 1fr">
        <div class="field"><label for="rb-name">Full name</label><input id="rb-name" type="text" required></div>
        <div class="field"><label for="rb-title">Title / role</label><input id="rb-title" type="text" placeholder="B.Tech Computer Science Student"></div>
      </div>
      <div class="subject-row" style="grid-template-columns:1fr 1fr">
        <div class="field"><label for="rb-email">Email</label><input id="rb-email" type="text"></div>
        <div class="field"><label for="rb-phone">Phone</label><input id="rb-phone" type="text"></div>
      </div>
      <div class="field"><label for="rb-summary">Professional summary</label><textarea id="rb-summary" placeholder="A short 2-3 line summary about you"></textarea></div>

      <h3>Education</h3>
      <div class="field"><label for="rb-education">Education (one entry per line, e.g. "B.Tech CSE, XYZ University, 2022-2026")</label><textarea id="rb-education"></textarea></div>

      <h3>Experience</h3>
      <div class="field"><label for="rb-experience">Experience (one entry per line)</label><textarea id="rb-experience"></textarea></div>

      <h3>Skills</h3>
      <div class="field"><label for="rb-skills">Skills (comma separated)</label><input id="rb-skills" type="text" placeholder="Python, SQL, Communication"></div>

      <h3>Projects & Certifications</h3>
      <div class="field"><label for="rb-projects">Projects / certifications (one per line)</label><textarea id="rb-projects"></textarea></div>

      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Generate & Download PDF</button>
        <button type="button" id="rb-reset" class="btn btn-secondary">Clear form</button>
      </div>
      <p class="field hint">Your resume data is saved only in this browser (local storage) so you don't lose progress &mdash; it is never sent to a server.</p>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    """
    script = """
    (function(){
      var FIELDS = ['rb-name','rb-title','rb-email','rb-phone','rb-summary','rb-education','rb-experience','rb-skills','rb-projects'];
      var STORE_KEY = 'tn_resume_draft';
      function save(){
        var data = {};
        FIELDS.forEach(function(id){ data[id] = document.getElementById(id).value; });
        try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); } catch(e){}
      }
      function load(){
        try {
          var data = JSON.parse(localStorage.getItem(STORE_KEY) || '{}');
          FIELDS.forEach(function(id){ if (data[id]) document.getElementById(id).value = data[id]; });
        } catch(e){}
      }
      load();
      FIELDS.forEach(function(id){ document.getElementById(id).addEventListener('input', save); });

      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
      }

      document.getElementById('rb-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var name = document.getElementById('rb-name').value.trim();
        if (!name) { showError('Please enter your full name.'); return; }
        if (typeof window.jspdf === 'undefined') { showError('The PDF library failed to load. Please check your internet connection and try again.'); return; }

        var doc = new window.jspdf.jsPDF({unit:'pt', format:'a4'});
        var margin = 48, y = 56, width = 495;
        function h1(text){ doc.setFont('helvetica','bold'); doc.setFontSize(20); doc.text(text, margin, y); y += 24; }
        function h2(text){ y += 6; doc.setFont('helvetica','bold'); doc.setFontSize(12); doc.setTextColor(20,99,86); doc.text(text.toUpperCase(), margin, y); doc.setTextColor(0,0,0); y += 4; doc.setDrawColor(20,99,86); doc.line(margin, y+4, margin+width, y+4); y += 16; }
        function body(text, size){
          doc.setFont('helvetica','normal'); doc.setFontSize(size||10.5);
          var lines = doc.splitTextToSize(text, width);
          lines.forEach(function(line){
            if (y > 780) { doc.addPage(); y = 56; }
            doc.text(line, margin, y); y += 14;
          });
        }
        h1(name);
        var title = document.getElementById('rb-title').value.trim();
        if (title) { doc.setFont('helvetica','normal'); doc.setFontSize(12); doc.text(title, margin, y); y += 18; }
        var contact = [document.getElementById('rb-email').value.trim(), document.getElementById('rb-phone').value.trim()].filter(Boolean).join('   |   ');
        if (contact) { doc.setFontSize(10); doc.setTextColor(90,90,90); doc.text(contact, margin, y); doc.setTextColor(0,0,0); y += 18; }

        var summary = document.getElementById('rb-summary').value.trim();
        if (summary) { h2('Summary'); body(summary); }

        var edu = document.getElementById('rb-education').value.trim();
        if (edu) { h2('Education'); edu.split('\\n').forEach(function(l){ if(l.trim()) body('\u2022 ' + l.trim()); }); }

        var exp = document.getElementById('rb-experience').value.trim();
        if (exp) { h2('Experience'); exp.split('\\n').forEach(function(l){ if(l.trim()) body('\u2022 ' + l.trim()); }); }

        var skills = document.getElementById('rb-skills').value.trim();
        if (skills) { h2('Skills'); body(skills); }

        var projects = document.getElementById('rb-projects').value.trim();
        if (projects) { h2('Projects & Certifications'); projects.split('\\n').forEach(function(l){ if(l.trim()) body('\u2022 ' + l.trim()); }); }

        doc.save((name.replace(/\\s+/g,'_') || 'resume') + '_resume.pdf');
        window.ToolNagri && window.ToolNagri.track('download_clicked', {tool:'resume-builder'});
      });

      document.getElementById('rb-reset').addEventListener('click', function(){
        if (!confirm('Clear all resume fields? This cannot be undone.')) return;
        document.getElementById('rb-form').reset();
        try { localStorage.removeItem(STORE_KEY); } catch(e){}
      });
    })();
    """
    build_tool_page(
        "resume-builder", panel, script,
        how_it_works="<p>Fill in your details and click generate &mdash; a clean, single-column resume PDF is created directly in your browser using an open-source PDF-generation library, then downloaded to your device. Your draft is auto-saved to your browser's local storage so you won't lose progress, but it is never uploaded to a server.</p>",
        example="<p>Fill in your name, education and skills, click 'Generate & Download PDF', and a ready-to-send resume PDF downloads immediately.</p>",
        faqs=[
            ("Do I need an account to save my resume?", "No. Your draft auto-saves in this browser's local storage. If you switch browsers or devices, or clear browsing data, the draft won't carry over &mdash; download your PDF to keep a permanent copy."),
            ("Is this resume ATS-friendly?", "The template uses a simple, single-column, text-based layout (no tables, icons, or graphics) which is generally easier for Applicant Tracking Systems to parse than heavily designed templates."),
        ],
        extra_head='<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>',
    )

    # ---------------- AI Text Rewriter (honest provider-abstraction stub) ----------------
    panel = """
    <div class="field"><label for="ai-input">Your text</label><textarea id="ai-input" rows="6" placeholder="Paste text you'd like rewritten..."></textarea></div>
    <div class="row-actions">
      <button type="button" id="ai-run" class="btn btn-primary">Rewrite with AI</button>
    </div>
    <div id="ai-result" class="notice" style="margin-top:16px">
      This tool is wired to a pluggable AI provider system, but no free AI provider is currently connected in this deployment.
      When a provider is configured, this box will show the rewritten text. In the meantime, the rest of the site's calculators
      and PDF tools work fully offline of any AI service.
    </div>
    """
    script = """
    (function(){
      // --- AIProvider abstraction (kept isolated so the rest of the site never depends on AI) ---
      // In production, wire ONE of these providers behind a serverless function that keeps API keys server-side.
      // Never call a paid or keyed API directly from this client-side file.
      var AIProvider = {
        FreeProvider: {
          available: false, // set true once a free-tier provider + serverless proxy is actually configured
          rewrite: async function(text){ throw new Error('no_provider_configured'); }
        }
      };
      var DAILY_LIMIT = 5; // configurable anonymous usage limit, enforced server-side in production
      document.getElementById('ai-run').addEventListener('click', async function(){
        var input = document.getElementById('ai-input').value.trim();
        var out = document.getElementById('ai-result');
        if (!input) { out.textContent = 'Please enter some text first.'; return; }
        if (!AIProvider.FreeProvider.available) {
          out.textContent = 'AI rewriting is not available yet in this deployment (no free AI provider is connected). Your text was not sent anywhere. Please check back once an AI provider is configured, or use the other tools on this site which all work without AI.';
          return;
        }
        try {
          out.textContent = 'Rewriting...';
          var result = await AIProvider.FreeProvider.rewrite(input);
          out.textContent = result;
        } catch (e) {
          out.textContent = 'The AI service is temporarily unavailable or you have reached today\\'s free usage limit. Please try again later.';
        }
      });
    })();
    """
    build_tool_page(
        "ai-text-rewriter", panel, script,
        how_it_works="<p>This tool is built on a pluggable <code>AIProvider</code> architecture so a free-tier AI provider can be connected later without changing the rest of the site. No paid API is required to launch, and the tool fails gracefully with a clear message when no provider is configured &mdash; it never breaks the page or silently pretends to work.</p>",
        example="<p>Once a provider is connected: paste a paragraph, click 'Rewrite with AI', and receive a reworded version, subject to a daily usage limit for anonymous users.</p>",
        faqs=[
            ("Why isn't this tool working yet?", "AI tools are deliberately isolated from the rest of the site so that connecting an AI provider is optional. This deployment does not yet have a free AI provider wired up on the backend, so the tool shows an honest status message rather than a broken or fake result."),
            ("Will this ever cost money to use?", "The goal is to keep a free tier available, likely with a daily usage limit for anonymous users, funded by ethical ads/premium features elsewhere on the site &mdash; not to promise unlimited free AI forever."),
        ],
        disclaimer="AI-generated text should always be reviewed before use. This tool does not send your text anywhere unless a provider is actively configured.",
    )
