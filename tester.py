import glob, cv2, requests, numpy as np, os
from bs4 import BeautifulSoup
from dom_col import get_dominant_colors, color_dict_HSV # type: ignore

SCRIPT_DIR = os.path.join(os.path.dirname(__file__))

table_row = '''
    <tr>
        <td>
            <img src="https://i.imgur.com/DWyjBd8.jpeg" style="border: 1px solid #000; max-width:300px; max-height:200px; display:block; margin:0 auto;" />
        </td>
        <td style="text-align: center; vertical-align: middle;">
            <p class="color-text">Yellow</p>
            <div style="width: 100%; display: table;">
                <div class="colors" style="display: table-row"></div>
            </div>
            <div class="squares"></div>
        </td>
        <td  style="text-align: center; vertical-align: middle;">
            <div class="color-info"></div>
        </td>
    </tr>
'''

main_html = '''
    <html>
        <head>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/jq-3.3.1/dt-1.10.25/datatables.min.css"/>
        </head>
        <body style="width:80%; margin:0 auto;">
            <table id="main-table" class="display">
                <thead>
                    <tr>
                        <th>Image</th>
                        <th>Colors</th>
                        <th>Info</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            
            </table>
            <script type="text/javascript" src="https://cdn.datatables.net/v/dt/jq-3.3.1/dt-1.10.25/datatables.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/unveil/1.3.0/jquery.unveil.min.js" integrity="sha512-smKadbDZ1g5bsWtP1BuWxgBq1WeP3Se1DLxeeBB+4Wf/HExJsJ3OV6lzravxS0tFd43Tp4x+zlT6/yDTtr+mew==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
            <script>
            $(document).ready(function() {
                $('#main-table').DataTable({
                    "drawCallback": function(settings) {
                        $("#main-table img:visible").unveil();
                    }
                }).on('page.dt', function() {
                    $('html, body').animate({
                        scrollTop: $(".dataTables_wrapper").offset().top
                    }, 'slow');
                });
            });

            </script>
        </body>
    </html>
'''



soup = BeautifulSoup(main_html, features="html.parser")

counter = 0

with open(os.path.join(SCRIPT_DIR, 'colours_test_images.csv')) as f:
    for url in f:

        if counter == 30: break # number of images to process
        else: counter += 1
        url = url.replace('prod-edit', 'prod-live')
        url = url.strip()

        resp = requests.get(url, verify=False)

        image = np.array(bytearray(resp.content), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        result, noColor, multiColor, numOfColors, text = get_dominant_colors(image)

        soup.tbody.append(BeautifulSoup(table_row, features="html.parser"))
        soup.find_all('p', {'class': 'color-text'})[-1].string = text

        color_info_div = soup.find_all('div', {'class': 'color-info'})[-1]
        
        for color, percentage in result:
            color_info_div.append(BeautifulSoup(f'<pre>{color:12} {percentage:6.2%}</pre>', features="html.parser"))

        soup.find_all('img')[-1]['data-src'] = url

        colors_div = soup.find_all('div', {'class': 'colors'})[-1]
        squares_dir = soup.find_all('div', {'class': 'squares'})[-1]

        if not noColor and not multiColor:
            total_percentage = sum(per for col, per in result[:numOfColors])

            for col, per in result[:numOfColors]:
                colors_div.append(BeautifulSoup(f'<div class="color-box" style="background-color:#{color_dict_HSV[col][2]}; height:50px; display:table-cell; width:{per/total_percentage:.2%}"></div>', features="html.parser"))
                squares_dir.append(BeautifulSoup(f'<div class="square" style="color:#{color_dict_HSV[col][2]}; font-size:6em; display:inline-block;">&#9632;</div>', features="html.parser"))



with open(os.path.join(SCRIPT_DIR, "result.html"), "w", encoding='utf-8') as f:
    f.write(soup.prettify())