MSSV: 202602978

# Lab 11 · Scenario Forge — báo cáo

Thị trấn của bạn (`meta.json: _run.town`): **D**

---

## 1. Phát lại log có trung thực không? (bước A)

Theo dữ liệu từ `evidence/replay.json`:
- Tổng số kịch bản: $n = 400$. Số kịch bản bị loại do chính người lái trong log gây va chạm: `dropped_human_crash_logs = 1` (sử dụng $n_{\text{used}} = 399$).
- **Khi chạy trên log phát lại (`replay`)**: có **96 va chạm** (`side: 4`, `rear: 92`, `front: 0`).
- **Khi chạy trong thế giới phản ứng (`reactive`)**: có **1 va chạm** (`side: 1`, `rear: 0`, `front: 0`).
- Số kịch bản bị va chạm ở cả hai môi trường: `crash_in_both = 0`.

**Giải thích:**
Phần lớn va chạm của log phát lại là va chạm phía sau (`rear`: 92/96 vụ), và đây là **va chạm giả (artefact)**. Trong log phát lại tĩnh, các xe xung quanh di chuyển mù quáng theo đúng tọa độ đã ghi của người lái người thật. Khi AV Planner của xe ta phản ứng thận trọng hơn người thật (phanh sớm và dứt khoát hơn), xe bám đuôi (TG) trong log phát lại không có cơ chế cảm nhận sự giảm tốc của xe ta nên vẫn lao tới theo quỹ đạo cũ và ủi vào đuôi xe ta. Ngược lại, trong thế giới phản ứng (`reactive`), xe TG được điều khiển bởi mô hình IDM nhận biết khoảng cách thu hẹp nên kịp thời đạp phanh theo, do đó số vụ va chạm đuôi giảm về 0.

**Kịch bản trong `replay_only`:**
Xét kịch bản số 8 (`replay.json: replay_only[1]`): va chạm dạng `rear` trong replay, nhưng trong môi trường phản ứng có `min_ttc_reactive = 2.52` s (rất an toàn). Ở kịch bản này, xe bám đuôi TG có `tgT = 0.74` s (bám rất sát). Khi xe ta phanh trước vạch người đi bộ (`pedT0 = 8.18` s), log tĩnh khiến TG đâm sầm vào đuôi xe ta, trong khi ở thế giới phản ứng, TG phanh tương ứng và duy trì khoảng cách tối thiểu an toàn.

---

## 2. Kịch bản bất khả thi (bước B)

Các luật kiểm tra trong `feasible.is_feasible` và căn cứ vật lý:
1. **Gia tốc ngang khi chuyển làn không vượt quá độ bám đường**: $a_{\text{lat}} = \left(\frac{\pi}{\text{cutDur}}\right)^2 \frac{3.5}{2} \le \mu g$. Quỹ đạo chuyển làn cosin qua quãng đường ngang $3.5\text{ m}$ đạt gia tốc uốn cực đại ở giữa quá trình. Nếu $a_{\text{lat}} > \mu g$, lực quán tính ly tâm vượt quá lực ma sát nghỉ tối đa giữa lốp và mặt đường, xe sẽ bị trượt mất lái thay vì chuyển làn.
2. **Gia tốc phanh sau nhập làn không vượt quá ma sát**: $\text{cutBrake} \le \mu g$. Theo định luật ma sát Coulomb, lực phanh cực đại của bánh xe là $F \le \mu m g$, do đó gia tốc hãm không thể vượt quá $\mu g$.
3. **Vận tốc người đi bộ trong giới hạn đi/chạy**: $\text{pedV} \le 2.5\text{ m/s}$ ($9\text{ km/h}$). Tốc độ đi bộ đô thị thường là $1.2 - 1.5\text{ m/s}$, tối đa khi chạy gấp cũng không thể vượt quá $2.5\text{ m/s}$.
4. **Vận tốc xe cắt làn hợp lệ**: $0 < \text{cutV} \le 22\text{ m/s}$ ($79.2\text{ km/h}$). Xe không thể lùi/đứng yên khi nhập làn vào dòng xe đang chạy và không vượt quá tốc độ tối đa cho phép trong đô thị.

**Trong `hunt.json`:**
- `bus_bypass`: bỏ qua 12 kịch bản bất khả thi.
- `cut_in`: bỏ qua 5 kịch bản bất khả thi.
- `crosswalk_block`: bỏ qua **15 kịch bản bất khả thi** (nhiều nhất).
- `rear_ended`: bỏ qua 3 kịch bản bất khả thi.

Cuộc săn `crosswalk_block` sinh nhiều kịch bản bất khả thi nhất vì hàm mục tiêu nguy hiểm kéo khoảng dừng an toàn `ped_room` về âm càng sâu càng tốt. Để tối đa hóa nguy cơ va chạm, thuật toán CEM đẩy vận tốc người đi bộ $\text{pedV}$ lên cực đại và dìm ma sát $\mu$ xuống đáy, khiến các mẫu ưu tú (elite) bị dồn về vùng vi phạm vật lý ($\text{pedV} > 2.5$ hoặc phanh vượt $\mu g$). Nếu **đếm** các kịch bản này là va chạm, xác suất rủi ro sẽ bị **thổi phồng giả tạo (overestimation)**, phạt planner vì những tình huống không thể xảy ra ngoài đời thực.

---

## 3. Monte Carlo cho bạn biết gì (bước C1)

Theo `evidence/mc.json`:
- Số lần thử nghiệm: $n = 3000$.
- Số vụ va chạm: $k = 0$.
- Tỷ lệ ước lượng: $\hat{p} = 0.0$.
- Khoảng tin cậy 95% Wilson: $[1.08 \times 10^{-19}, 1.28 \times 10^{-3}]$.

**Số lần chạy cần để khoảng tin cậy hẹp còn $\pm 20\%$ của $p$:**
Nửa độ rộng khoảng tin cậy $z \sqrt{\frac{p(1-p)}{n}} \le 0.20 p \implies n \ge \frac{z^2}{0.04 p} \approx \frac{96}{p}$.
- Nếu lấy theo cận trên của Wilson ($p \approx 1.28 \times 10^{-3}$): cần $n \approx \frac{96}{1.28 \times 10^{-3}} \approx 75\,000$ lần chạy.
- Nếu lấy theo giá trị thực tế tìm được ở bước C3 ($p \approx 5 \times 10^{-4}$): cần $n \approx \frac{96}{5 \times 10^{-4}} \approx 192\,000$ lần chạy.

Trong 3 000 lần chạy ngẫu nhiên, **toàn bộ các kiểu thất bại** (`bus_bypass`, `cut_in`, `crosswalk_block`, `rear_ended`, `other`) đều **chưa hề xuất hiện** ($k = 0$). Con số đúng cần báo không được phép là 0, mà phải báo bằng cận trên khoảng tin cậy Wilson 95%: $p \le 1.28 \times 10^{-3}$ (hoặc quy tắc Rule of Three: $3/n = 3/3000 = 1.0 \times 10^{-3}$).

---

## 4. Importance sampling, ESS và độ suy biến (bước C3)

Bảng tổng hợp từ `evidence/estimate.json` ($n = 600$ mỗi mode/seed):

| Kiểu thất bại | Seed | $p$ | hits | ess | top_share |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **bus_bypass** | 0 | $5.22 \times 10^{-4}$ | 40 | 130.9 | 0.322 |
| | 1 | $2.19 \times 10^{-4}$ | 36 | 127.1 | 0.161 |
| | 2 | $7.88 \times 10^{-4}$ | 35 | 111.7 | 0.291 |
| **crosswalk_block** | 0 | $2.50 \times 10^{-7}$ | 118 | 131.0 | 0.259 |
| | 1 | $2.36 \times 10^{-6}$ | 124 | 122.1 | **0.712** |
| | 2 | $3.68 \times 10^{-7}$ | 125 | 105.0 | 0.438 |
| **cut_in** | 0, 1, 2 | 0.0 (cận trên $0.025$) | 0 | 123 – 153 | 0.0 |
| **rear_ended** | 0, 1, 2 | 0.0 (cận trên $0.025$) | 0 | 115 – 123 | 0.0 |
| **Tổng (`total`)** | 0 | $5.22 \times 10^{-4}$ | — | — | — |
| | 1 | $2.21 \times 10^{-4}$ | — | — | — |
| | 2 | $7.88 \times 10^{-4}$ | — | — | — |

**Nhận xét:**
- Ba seed có đồng thuận với nhau về độ lớn tổng quát ($2.21 \times 10^{-4} - 7.88 \times 10^{-4}$, chênh nhau $\sim 3.5$ lần, đúng với tính chất ngẫu nhiên phân tán của CEM IS). Cả ba seed đều đồng thuận với Monte Carlo vì đều nằm dưới cận trên Wilson $1.28 \times 10^{-3}$.
- `top_share` lớn ($> 0.5$) xảy ra ở **Seed 1** của `crosswalk_block` (**0.712**). Khi phân phối $q$ co lại quá hẹp, hầu hết các mẫu rút ra có mật độ tự nhiên $p(u)$ cực thấp (trọng số $w = p/q$ rất nhỏ). Chỉ cần một mẫu trúng vùng có $p(u)$ tương đối cao thì trọng số của riêng mẫu đó đã gánh tới $71.2\%$ toàn bộ giá trị ước lượng, biến con số trở thành đóng góp đơn lẻ của một mẫu duy nhất.
- Ngân sách IS là `budget = 16 800` lần chạy, tiết kiệm hơn 11 lần so với $\sim 192\,000$ lần chạy của Monte Carlo để đạt cùng biên độ tin cậy.
- Phần `other` lấy từ kết quả Monte Carlo C1 (`estimate.json: other`, $k = 0, n = 3000$, cận trên $1.28 \times 10^{-3}$). Ta không săn `other` vì CEM đòi hỏi hàm điểm nguy hiểm cụ thể; "other" bao gồm mọi tình huống không xác định trước nên không có một metric nguy hiểm duy nhất nào để dẫn dắt phân phối đề xuất.

---

## 5. Các kiểu thất bại (bước C2 + 3D)

Hai kiểu thất bại tìm thấy:
1. **`bus_bypass`** (110 vụ trong `hunt.json`):
   - ![Va chạm lách xe buýt](shots/bus_bypass.jpg)
   - *Chuỗi sự kiện:* Xe buýt đỗ ở làn E2 che khuất hoàn toàn tầm nhìn của xe ta ở làn E1; xe C2 từ sau xe buýt lách sang làn E1 với tốc độ thấp để vượt qua xe buýt; do điểm mù lớn, planner của xe ta nhận diện C2 quá trễ và không kịp phanh, dẫn đến va chạm góc đầu xe.
2. **`crosswalk_block`** (92 vụ trong `hunt.json`):
   - ![Chặn vạch người đi bộ](shots/crosswalk_block.jpg)
   - *Chuỗi sự kiện:* Người đi bộ P1 bước ra vạch qua đường từ sau xe buýt đỗ; planner phát hiện người đi bộ muộn nên kích hoạt phanh gấp khẩn cấp; xe dừng lại hoàn toàn nhưng thân xe đã trườn vào vạch sang đường, chắn ngang lối đi của P1 buộc người đi bộ phải đứng lại.

**Kiểu không tìm thấy:**
`cut_in` (0 vụ thuần túy, chỉ có 10 vụ lách xe buýt) và `rear_ended` (0 vụ). Ta tin tưởng kết quả này ở mức độ cao: trong môi trường phản ứng, xe bám đuôi TG lái theo IDM có khoảng cách an toàn nên không thể tự tông đuôi xe ta; còn xe C2 chỉ nhập làn khi có khe hở chấp nhận được (`gap acceptance`), trừ khi bị dồn vào điểm mù của xe buýt thì lại được phân loại ưu tiên vào `bus_bypass`.

Nếu chỉ chạy **một cuộc săn chung**, thuật toán CEM sẽ bị **suy biến về một kiểu (mode collapse)**: hàm nguy hiểm của kiểu dễ va chạm nhất (`bus_bypass`) sẽ kéo toàn bộ phân phối đề xuất $q$ về phía nó, khiến cuộc săn chỉ tìm thấy duy nhất kiểu đó và bỏ sót hoàn toàn các kiểu còn lại (điều này thể hiện rõ khi săn `cut_in`, thuật toán vẫn bị hút về 10 vụ `bus_bypass`).

---

## 6. Sửa planner (bước E + 3D)

Theo dữ liệu từ `evidence/fix.json`:
- **Policy được chọn**: `{'cutinLat': 2.6}` (tăng ngưỡng ngang coi xe lấn làn là xe trước từ $2.15\text{ m}$ lên $2.6\text{ m}$).
- **Trên TRAIN**:
  - Bản chọn: `fail = 7.18e-07`, `fail_hi = 1.43e-06`, `progress = 218.32 m`.
  - Baseline: `fail = 1.73e-03`, `fail_hi = 3.99e-03`, `progress = 218.32 m`.
- **Trên TEST**:
  - Bản sửa (`chosen`): `fail = 1.34e-05`, `fail_hi_seen = 3.86e-05`, `fail_hi = 1.32e-03`, `progress = 216.63 m`, `harsh = 7.67`.
  - Bản gốc (`baseline`): `fail = 2.76e-04`, `fail_hi_seen = 4.40e-04`, `fail_hi = 1.72e-03`, `progress = 216.63 m`, `harsh = 7.97`.

![Bản sửa tránh được va chạm so với bóng mờ baseline](shots/ghost_avoidance.jpg)

**Vì sao `fail_hi` bản sửa ($1.32 \times 10^{-3}$) có thể lớn hơn `fail` gốc ($2.76 \times 10^{-4}$):**
`fail` là ước lượng điểm, còn `fail_hi` là cận trên 95% hợp lệ bao gồm cả phần bù $3/(0.2 \cdot n)$ cho các kiểu chưa quan sát thấy trên mẫu hữu hạn ($n=400$). Với $n=400$, bất kỳ ước lượng nào cũng có độ bất định tối thiểu cỡ $10^{-3}$. Tuy vậy, so sánh công bằng cận trên hợp lệ `fail_hi` của cả hai trên TEST thì bản sửa ($1.32 \times 10^{-3}$) vẫn thấp hơn bản gốc ($1.72 \times 10^{-3}$), và tỷ lệ lỗi `fail` thực tế giảm hơn 20 lần (từ $2.76 \times 10^{-4}$ xuống $1.34 \times 10^{-5}$) mà không làm suy giảm quãng đường (giữ nguyên $216.63\text{ m}$).

**Núm chỉnh "an toàn hơn" nhưng phản tác dụng:**
Ví dụ ứng viên `{'cautionV': 5.0}`: giảm tốc độ thận trọng khi qua vạch bị che xuống $5\text{ m/s}$. Tưởng chừng đi chậm hơn sẽ an toàn hơn, nhưng thực tế quãng đường giảm mạnh xuống $173.1\text{ m}$ (mất hơn $20\%$ tiến độ). Xe chạy quá chậm và rề rà khiến xe sau bám sát hoặc xe cắt làn C2 mất kiên nhẫn tạt đầu ở góc hẹp, gián tiếp làm tăng mức độ nguy hiểm do các tác nhân xung quanh phản ứng tiêu cực lại hành vi của xe ta. Tương tự, nếu tăng `T` lên 2.0s (`T: 2.0`), `fail` trên TRAIN lại tăng lên $2.12 \times 10^{-3}$ do nhường khoảng cách quá lớn phía trước kích thích xe khác chèn vào.

---

## 7. Từ mô phỏng ra đường thật

Ba giả định ảnh hưởng lớn nhất trong `space.py`:
1. **Khoảng cách chấp nhận nhập làn (`cutGap`) của xe chuyển làn C2**:
   - *Dữ liệu thật thay thế:* Phân phối khoảng cách nhập làn trích xuất từ video flycam của các tập dữ liệu tự nhiên như **highD** hoặc **INTERACTION dataset**.
   - *Hướng sai lệch:* Nếu lái xe ngoài đời thực hung hăng hơn (chấp nhận khe hẹp hơn), số vụ va chạm ngoài đời sẽ **cao hơn** số mô phỏng báo cáo.
2. **Tỷ lệ người đi bộ ngó qua xe buýt (`pedLook`)**:
   - *Dữ liệu thật thay thế:* Dữ liệu theo dõi ánh mắt và quỹ đạo tiếp cận của người đi bộ gần xe buýt công cộng từ tập dữ liệu **PIE (Pedestrian Intent Estimation)**.
   - *Hướng sai lệch:* Nếu ngoài đời người đi bộ ít ngó nghiêng hơn (bước thẳng ra đường do ỷ lại vạch ưu tiên), số vụ `crosswalk_block` thực tế sẽ **cao hơn nhiều**.
3. **Phân phối hệ số ma sát mặt đường ($\mu$)**:
   - *Dữ liệu thật thay thế:* Thống kê khí tượng thủy văn về tần suất mưa và dữ liệu đo ma sát mặt đường lốp thực tế của cơ quan giao thông địa phương.
   - *Hướng sai lệch:* Giả định đang dùng $\mu \in \{0.5, 0.8\}$. Nếu khu vực thực tế có đường trơn dầu hoặc tuyết ($\mu < 0.35$), quãng đường phanh thực tế dài hơn nhiều và xác suất va chạm sẽ **tăng vọt**.

---

## 8. Giới hạn

Ba điều xác suất báo cáo **không** phản ánh:
1. **Hình học đường và hạ tầng giao thông lý tưởng hóa**: Mô phỏng chỉ có một đoạn phố thẳng phẳng 2 làn với 1 vạch qua đường; không có dốc, cua khuất tầm nhìn, ngã tư đèn tín hiệu, nắp cống gồ ghề hay xe đỗ chắn lề ngẫu nhiên.
2. **Hành vi tác nhân đồng nhất (chỉ theo IDM)**: Các xe khác chỉ lái theo IDM thuần túy, không mô phỏng được hành vi người thật như mất tập trung lướt điện thoại, lái xe khi say rượu, hay cố tình chèn ép xe tự lái.
3. **Cảm biến và thị giác hoàn hảo**: Mô phỏng giả định tầm nhìn hình học tuyệt đối (không bị che thì phát hiện 100% không độ trễ), bỏ qua nhiễu cảm biến, độ trễ nhận diện (perception latency 100–300 ms), và hiện tượng nhận diện nhầm do ánh sáng yếu hay thời tiết xấu.

**Nếu được thêm một tuần:**
Tôi sẽ đo lường độ nhạy của tỷ lệ va chạm đối với **độ trễ nhận diện và ra quyết định (perception-to-actuation latency)** từ $50\text{ ms}$ đến $400\text{ ms}$, đồng thời bổ sung các tác nhân xe máy/xe đạp di chuyển len lỏi giữa hai làn xe (lane splitting).

---

## 9. Rắc rối của bạn (bước G + chương 10)

- **Rắc rối:** Tình huống người đi xe đạp (`bike`) di chuyển ở làn bên cạnh (làn E2), khi xe ta tiếp cận từ phía sau thì xe đạp bất ngờ lạng mạnh sang trái $2.2 - 2.8\text{ m}$ vào thẳng làn E1 của xe ta để tránh chướng ngại vật/ổ gà ở mép đường. Ngoài đời, đây là tình huống rất hay gặp trên các tuyến đường đô thị hỗn hợp.
- **Căn cứ:** Planner IDM chỉ giám sát các vật thể nằm trong hành lang làn E1 (`cutinLat`). Khi xe đạp ở làn E2 lạng sang ở khoảng cách gần ($12 - 18\text{ m}$), planner chỉ phanh theo phản ứng tiện nghi của IDM ($b = 2.0\text{ m/s}^2$) thay vì phanh khẩn cấp hết cỡ, dẫn đến va chạm.
- **Giả định (`hazard.json`):**
  - `space`: `h0_x` $\in [5.0, 35.0]\text{ m}$, `h0_swerve` $\in [2.2, 2.8]\text{ m}$, `h0_trig` $\in [12.0, 18.0]\text{ m}$.
  - `exposure`: $0.02$ lần/chuyến đi (ước tính trung bình 1 lần trên 50 chuyến đi đô thị).
  - Căn cứ vật lý: Thời gian lạng $2.2\text{ s}$ tương ứng gia tốc ngang đỉnh $a_{\text{lat}} = (\pi / 2.2)^2 \times 2.8 / 2 \approx 2.85\text{ m/s}^2 < 3.0\text{ m/s}^2$ (giới hạn vật lý lạng xe đạp).
- **Kết quả (theo `evidence/mine.json`):**
  - Tỷ lệ kịch bản khả thi: `accepted = 99.53%` (1 493 / 1 500 kịch bản).
  - Cảnh gốc: va chạm lúc $t = 7.15\text{ s}$ giữa xe ta và H0.
  - **Policy gốc (`baseline`)**:
    - Tổng va chạm: **922** = 919 `avoidable` + 3 `unavoidable` + 0 `unattributed` (0 vụ ở tốc độ $< 1\text{ m/s}$).
    - $P(\text{lỗi planner} \mid \text{hazard}) = 61.55\%$ (Khoảng Wilson 95%: $[59.06\%, 63.99\%]$).
    - Tần suất mỗi chuyến: $1.23 \times 10^{-2}$ lần/chuyến (cận trên $1.28 \times 10^{-2}$).
  - **Policy chọn (`chosen`, `cutinLat: 2.6`)**:
    - Tổng va chạm: **375** = 373 `avoidable` + 2 `unavoidable` + 0 `unattributed` (0 vụ ở tốc độ $< 1\text{ m/s}$).
    - $P(\text{lỗi planner} \mid \text{hazard}) = 24.98\%$ (Khoảng Wilson 95%: $[22.85\%, 27.24\%]$).
    - Tần suất mỗi chuyến: $5.00 \times 10^{-3}$ lần/chuyến (cận trên $5.45 \times 10^{-3}$).
  - So sánh với lách xe buýt: Tần suất gặp sự cố do xe đạp lạng ra ($5.00 \times 10^{-3}$) cao gấp gần 10 lần so với sự cố lách xe buýt ($5.22 \times 10^{-4}$).

![Kịch bản xe đạp lạng ra tại Chương 10](shots/hazard_bike.jpg)

- **Chuẩn "tránh được" (`avoidable`) là chuẩn lạc quan:**
  Chuẩn `avoidable` là lạc quan vì nó giả định xe nhận biết được rắc rối ngay tại thời điểm bắt đầu nhìn thấy và đạp phanh tối đa ở giới hạn bám $\mu g$. Một planner thực tế không thể đạp phanh khẩn cấp tối đa mỗi khi có phương tiện di chuyển ở làn bên cạnh. Mặt khác, chuẩn này bi quan ở chỗ nó chỉ thử nghiệm hành động phanh mà không thử đánh lái tránh chướng ngại vật (nhiều tình huống chỉ cần lách nhẹ vài chục cm là tránh được).
- **Bạn tự lái thì sao:**
  Khi người lái tự điều khiển bằng pedal trong Chương 10, người lái phát hiện góc đánh lái và xu hướng tiến vào làn của xe đạp từ sớm, chủ động nhả ga và rà nhẹ phanh từ xa, hoàn toàn tránh được va chạm một cách êm ái mà không cần phanh khẩn cấp ở ngưỡng lốp như planner.
- **Cách sửa:**
  - *Núm chỉnh:* Việc tăng `cutinLat` lên $2.6\text{ m}$ ở Bước E đã giúp mở rộng hành lang nhận diện, giúp xe nhận diện xe đạp lấn làn sớm hơn và giảm tỷ lệ lỗi từ $61.55\%$ xuống $24.98\%$.
  - *Logic mới cần bổ sung:* Cần bổ sung mô-đun **dự đoán quỹ đạo ngắn hạn dựa trên vận tốc ngang ($v_{\text{lat}}$)** của các phương tiện ở làn bên cạnh. Nếu phát hiện xe đạp ở làn ngoài có xu hướng lạng vào làn xe ta với vận tốc ngang lớn, planner cần chủ động giảm tốc độ phòng ngừa (proactive coasting/braking) ngay trước khi xe đạp cắt qua ranh giới `cutinLat`.
