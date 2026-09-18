from build import build_tool_page

def register():
    # ---------------- Age Calculator ----------------
    panel = """
    <form id="age-form">
      <div class="field"><label for="dob">Date of birth</label><input id="dob" type="date" required></div>
      <div class="field"><label for="asof">Calculate age as of</label><input id="asof" type="date"></div>
      <p class="field hint">Leave "as of" blank to use today's date.</p>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate Age</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Your age</div>
      <div class="big" id="age-value">-</div>
      <div class="result-grid">
        <div class="item"><div class="label">Total days lived</div><div class="val" id="age-days">-</div></div>
        <div class="item"><div class="label">Total months</div><div class="val" id="age-months">-</div></div>
      </div>
    </div>
    """
    script = """
    (function(){
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('age-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var dobStr = document.getElementById('dob').value;
        var asofStr = document.getElementById('asof').value;
        if (!dobStr) { showError('Please select a date of birth.'); return; }
        var dob = new Date(dobStr + 'T00:00:00');
        var asof = asofStr ? new Date(asofStr + 'T00:00:00') : new Date();
        asof.setHours(0,0,0,0);
        if (dob > asof) { showError('Date of birth cannot be after the "as of" date.'); return; }
        function daysInMonth(y, m) { return new Date(y, m+1, 0).getDate(); }
        function addMonthsClamped(baseY, baseM, baseD, monthsToAdd) {
          var totalM = baseM + monthsToAdd;
          var y = baseY + Math.floor(totalM/12);
          var m = ((totalM % 12) + 12) % 12;
          var d = Math.min(baseD, daysInMonth(y, m));
          return new Date(y, m, d);
        }
        var totalMonths = (asof.getFullYear()-dob.getFullYear())*12 + (asof.getMonth()-dob.getMonth());
        var candidate = addMonthsClamped(dob.getFullYear(), dob.getMonth(), dob.getDate(), totalMonths);
        if (candidate > asof) { totalMonths -= 1; candidate = addMonthsClamped(dob.getFullYear(), dob.getMonth(), dob.getDate(), totalMonths); }
        var years = Math.floor(totalMonths/12);
        var months = totalMonths - years*12;
        var days = Math.round((asof - candidate)/86400000);
        var totalDays = Math.round((asof - dob) / 86400000);
        var totalMonths = years*12 + months;
        document.getElementById('age-value').textContent = years + ' yr ' + months + ' mo ' + days + ' d';
        document.getElementById('age-days').textContent = totalDays.toLocaleString('en-IN');
        document.getElementById('age-months').textContent = totalMonths.toLocaleString('en-IN');
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('age-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "age-calculator", panel, script,
        how_it_works="<p>We calculate the exact difference between your date of birth and the reference date (today, unless you choose another date), broken down into full years, months and days, accounting for varying month lengths and leap years.</p>",
        example="<p>Someone born on 15 August 2000, calculated as of 14 September 2026, is 26 years, 0 months and 30 days old.</p>",
        faqs=[
            ("Does this account for leap years?", "Yes, the calculation is based on actual calendar dates, so leap years are automatically handled correctly."),
            ("Can I calculate age as of a future or past date?", "Yes, use the 'Calculate age as of' field to pick any date, not just today."),
        ],
    )

    # ---------------- BMI Calculator ----------------
    panel = """
    <form id="bmi-form">
      <div class="field">
        <label for="bmi-units">Units</label>
        <select id="bmi-units">
          <option value="metric">Metric (kg, cm)</option>
          <option value="imperial">Imperial (lb, in)</option>
        </select>
      </div>
      <div class="field"><label for="bmi-weight">Weight</label><input id="bmi-weight" type="number" min="0" step="0.1" placeholder="65" required></div>
      <div class="field"><label for="bmi-height">Height</label><input id="bmi-height" type="number" min="0" step="0.1" placeholder="170" required></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate BMI</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Your BMI</div>
      <div class="big" id="bmi-value">-</div>
      <p id="bmi-category" style="margin-top:8px;font-weight:600"></p>
    </div>
    """
    script = """
    (function(){
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('bmi-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var units = document.getElementById('bmi-units').value;
        var w = parseFloat(document.getElementById('bmi-weight').value);
        var h = parseFloat(document.getElementById('bmi-height').value);
        if (isNaN(w) || isNaN(h)) { showError('Please enter both weight and height.'); return; }
        if (w <= 0 || h <= 0) { showError('Weight and height must be greater than zero.'); return; }
        var bmi;
        if (units === 'metric') {
          var hM = h/100;
          bmi = w / (hM*hM);
        } else {
          bmi = 703 * w / (h*h);
        }
        if (!isFinite(bmi) || bmi <= 0 || bmi > 200) { showError('Please check your height and weight values.'); return; }
        var cat, color;
        if (bmi < 18.5) { cat = 'Underweight'; }
        else if (bmi < 25) { cat = 'Normal weight'; }
        else if (bmi < 30) { cat = 'Overweight'; }
        else { cat = 'Obese'; }
        document.getElementById('bmi-value').textContent = bmi.toFixed(1);
        document.getElementById('bmi-category').textContent = cat + ' (WHO general adult classification)';
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('bmi-form').reset();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "bmi-calculator", panel, script,
        how_it_works="<p>BMI (Body Mass Index) is calculated as weight (kg) &divide; height (m)&sup2; in metric units, or 703 &times; weight (lb) &divide; height (in)&sup2; in imperial units. It is a simple screening measure, not a diagnostic tool.</p>",
        example="<p>A person weighing 65 kg at 170 cm height has a BMI of 65 &divide; 1.7&sup2; = <strong>22.5</strong>, which falls in the 'Normal weight' range.</p>",
        faqs=[
            ("Is BMI accurate for everyone?", "BMI does not account for muscle mass, bone density, age, sex or body composition, so it can be misleading for athletes, older adults, and some other groups. It's a general population screening tool, not a diagnosis."),
            ("What BMI range is considered healthy?", "The WHO general classification considers 18.5&ndash;24.9 as the normal weight range for most adults, though this can vary by population and individual factors."),
        ],
        disclaimer="This BMI calculator provides a general estimate and is not medical advice or a diagnosis. Consult a qualified healthcare professional for personal health guidance.",
    )

    # ---------------- Percentage Calculator ----------------
    panel = """
    <form id="pct-form">
      <div class="field">
        <label for="pct-mode">What do you want to calculate?</label>
        <select id="pct-mode">
          <option value="basic">X% of Y</option>
          <option value="marks">Marks percentage (obtained / total)</option>
          <option value="change">Percentage change (from X to Y)</option>
        </select>
      </div>
      <div id="pct-inputs"></div>
      <div class="row-actions">
        <button type="submit" class="btn btn-primary">Calculate</button>
        <button type="button" id="reset-btn" class="btn btn-secondary">Reset</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card hidden">
      <div class="label">Result</div>
      <div class="big" id="pct-value">-</div>
    </div>
    """
    script = """
    (function(){
      var modeSel = document.getElementById('pct-mode');
      var inputsEl = document.getElementById('pct-inputs');
      var TEMPLATES = {
        basic: '<div class="field"><label for="p1">Percentage (%)</label><input id="p1" type="number" step="0.01" placeholder="20"></div><div class="field"><label for="p2">Of value</label><input id="p2" type="number" step="0.01" placeholder="500"></div>',
        marks: '<div class="field"><label for="p1">Marks obtained</label><input id="p1" type="number" step="0.01" placeholder="450"></div><div class="field"><label for="p2">Total marks</label><input id="p2" type="number" step="0.01" placeholder="500"></div>',
        change: '<div class="field"><label for="p1">Original value</label><input id="p1" type="number" step="0.01" placeholder="200"></div><div class="field"><label for="p2">New value</label><input id="p2" type="number" step="0.01" placeholder="250"></div>'
      };
      function render(){ inputsEl.innerHTML = TEMPLATES[modeSel.value]; }
      modeSel.addEventListener('change', render);
      render();
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
        document.getElementById('result-box').classList.add('hidden');
      }
      document.getElementById('pct-form').addEventListener('submit', function(e){
        e.preventDefault();
        document.getElementById('error-box').classList.add('hidden');
        var a = parseFloat(document.getElementById('p1').value);
        var b = parseFloat(document.getElementById('p2').value);
        if (isNaN(a) || isNaN(b)) { showError('Please fill in both fields.'); return; }
        var mode = modeSel.value, result, text;
        if (mode === 'basic') {
          result = (a/100)*b;
          text = a + '% of ' + b + ' = ' + result.toFixed(2);
        } else if (mode === 'marks') {
          if (b === 0) { showError('Total marks cannot be zero.'); return; }
          if (a < 0 || b < 0) { showError('Marks cannot be negative.'); return; }
          if (a > b) { showError('Marks obtained cannot exceed total marks.'); return; }
          result = (a/b)*100;
          text = result.toFixed(2) + '%';
        } else {
          if (a === 0) { showError('Original value cannot be zero for percentage change.'); return; }
          result = ((b-a)/Math.abs(a))*100;
          text = (result >= 0 ? '+' : '') + result.toFixed(2) + '%';
        }
        document.getElementById('pct-value').textContent = text;
        document.getElementById('result-box').classList.remove('hidden');
      });
      document.getElementById('reset-btn').addEventListener('click', function(){
        document.getElementById('pct-form').reset();
        render();
        document.getElementById('result-box').classList.add('hidden');
        document.getElementById('error-box').classList.add('hidden');
      });
    })();
    """
    build_tool_page(
        "percentage-calculator", panel, script,
        how_it_works="<p>This tool covers three common percentage calculations: a basic X% of Y, exam-style marks percentage (obtained &divide; total &times; 100), and percentage change between two values ((new - old) &divide; |old| &times; 100).</p>",
        example="<p>450 marks out of 500 gives 90%. A value moving from 200 to 250 is a +25% change.</p>",
        faqs=[
            ("Can percentage change be negative?", "Yes &mdash; if the new value is smaller than the original, the result will be negative, indicating a decrease."),
        ],
    )

    # ---------------- Unit Converter ----------------
    panel = """
    <form id="uc-form">
      <div class="field">
        <label for="uc-category">Category</label>
        <select id="uc-category"></select>
      </div>
      <div class="subject-row" style="grid-template-columns:1fr 1fr">
        <div class="field"><label for="uc-value">Value</label><input id="uc-value" type="number" step="any" value="1"></div>
        <div class="field"><label for="uc-from">From</label><select id="uc-from"></select></div>
      </div>
      <div class="field"><label for="uc-to">To</label><select id="uc-to"></select></div>
      <div class="row-actions">
        <button type="button" id="uc-swap" class="btn btn-secondary">&#8646; Swap units</button>
      </div>
    </form>
    <div id="error-box" class="error-msg hidden"></div>
    <div id="result-box" class="result-card">
      <div class="label">Converted value</div>
      <div class="big" id="uc-result">-</div>
    </div>
    """
    script = """
    (function(){
      var UNITS = {
        length: {base:'m', units:{ 'Millimetre (mm)':0.001,'Centimetre (cm)':0.01,'Metre (m)':1,'Kilometre (km)':1000,'Inch (in)':0.0254,'Foot (ft)':0.3048,'Yard (yd)':0.9144,'Mile (mi)':1609.344 }},
        weight: {base:'kg', units:{ 'Milligram (mg)':0.000001,'Gram (g)':0.001,'Kilogram (kg)':1,'Tonne (t)':1000,'Ounce (oz)':0.0283495,'Pound (lb)':0.453592 }},
        temperature: {special:true},
        area: {base:'sqm', units:{ 'Sq. Metre (m2)':1,'Sq. Kilometre (km2)':1000000,'Sq. Foot (ft2)':0.092903,'Acre':4046.86,'Hectare':10000 }},
        volume: {base:'l', units:{ 'Millilitre (ml)':0.001,'Litre (l)':1,'Cubic Metre (m3)':1000,'US Gallon (gal)':3.78541,'Cup':0.24 }},
        speed: {base:'mps', units:{ 'Metres/sec (m/s)':1,'Kilometres/hour (km/h)':0.277778,'Miles/hour (mph)':0.44704,'Knot':0.514444 }},
        time: {base:'s', units:{ 'Second (s)':1,'Minute (min)':60,'Hour (hr)':3600,'Day':86400,'Week':604800 }},
        data: {base:'byte', units:{ 'Byte (B)':1,'Kilobyte (KB)':1024,'Megabyte (MB)':1048576,'Gigabyte (GB)':1073741824,'Terabyte (TB)':1099511627776 }}
      };
      var catSel = document.getElementById('uc-category');
      var fromSel = document.getElementById('uc-from');
      var toSel = document.getElementById('uc-to');
      Object.keys(UNITS).forEach(function(k){
        var opt = document.createElement('option'); opt.value = k; opt.textContent = k.charAt(0).toUpperCase()+k.slice(1);
        catSel.appendChild(opt);
      });
      function populateUnitSelects(){
        var cat = catSel.value;
        fromSel.innerHTML = ''; toSel.innerHTML = '';
        var names = cat === 'temperature' ? ['Celsius (\u00b0C)','Fahrenheit (\u00b0F)','Kelvin (K)'] : Object.keys(UNITS[cat].units);
        names.forEach(function(n, i){
          var o1 = document.createElement('option'); o1.value=n; o1.textContent=n; fromSel.appendChild(o1);
          var o2 = document.createElement('option'); o2.value=n; o2.textContent=n; toSel.appendChild(o2);
        });
        toSel.selectedIndex = names.length > 1 ? 1 : 0;
        convert();
      }
      function toCelsius(v, unit){
        if (unit.indexOf('Celsius') === 0) return v;
        if (unit.indexOf('Fahrenheit') === 0) return (v-32)*5/9;
        return v - 273.15;
      }
      function fromCelsius(c, unit){
        if (unit.indexOf('Celsius') === 0) return c;
        if (unit.indexOf('Fahrenheit') === 0) return c*9/5+32;
        return c + 273.15;
      }
      function showError(msg){
        document.getElementById('error-box').textContent = msg;
        document.getElementById('error-box').classList.remove('hidden');
      }
      function convert(){
        document.getElementById('error-box').classList.add('hidden');
        var cat = catSel.value;
        var val = parseFloat(document.getElementById('uc-value').value);
        if (isNaN(val)) { showError('Please enter a numeric value.'); document.getElementById('uc-result').textContent='-'; return; }
        var result;
        if (cat === 'temperature') {
          if (fromSel.value.indexOf('Kelvin')===0 && val < 0) { showError('Kelvin cannot be negative.'); return; }
          var c = toCelsius(val, fromSel.value);
          result = fromCelsius(c, toSel.value);
        } else {
          var table = UNITS[cat].units;
          var baseVal = val * table[fromSel.value];
          result = baseVal / table[toSel.value];
        }
        document.getElementById('uc-result').textContent = (Math.round(result*1e6)/1e6).toLocaleString('en-IN', {maximumFractionDigits:6});
      }
      catSel.addEventListener('change', populateUnitSelects);
      fromSel.addEventListener('change', convert);
      toSel.addEventListener('change', convert);
      document.getElementById('uc-value').addEventListener('input', convert);
      document.getElementById('uc-swap').addEventListener('click', function(){
        var f = fromSel.value; fromSel.value = toSel.value; toSel.value = f; convert();
      });
      populateUnitSelects();
    })();
    """
    build_tool_page(
        "unit-converter", panel, script,
        how_it_works="<p>For most categories, each unit is converted to a common base unit (like metres for length, or kilograms for weight) using standard conversion factors, then converted to the target unit. Temperature uses direct formulas between Celsius, Fahrenheit and Kelvin since they don't share a simple multiplicative base.</p>",
        example="<p>10 kilometres converts to 6.21 miles. 100&deg;C converts to 212&deg;F.</p>",
        faqs=[
            ("Which categories are supported?", "Length, weight, temperature, area, volume, speed, time and data storage, covering the most commonly needed everyday and academic conversions."),
        ],
    )
