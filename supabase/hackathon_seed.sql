-- Presentation dataset for Smart Campus Management.
-- Run schema.sql first. Run this file only when you want populated hackathon data.
-- The records are fictional and may be safely removed after a presentation.

insert into public.profiles (id, name, email, role, access_code_hash) values
('a1000000-0000-0000-0000-000000000001','Ananya Rao','ananya.rao@campus.example','faculty',encode(digest('CSE2026','sha256'),'hex')),
('a1000000-0000-0000-0000-000000000002','Vikram Shah','vikram.shah@campus.example','faculty',encode(digest('CSE2027','sha256'),'hex')),
('a1000000-0000-0000-0000-000000000003','Meera Iyer','meera.iyer@campus.example','faculty',encode(digest('CSE2028','sha256'),'hex')),
('a1000000-0000-0000-0000-000000000004','Karan Patel','karan.patel@campus.example','faculty',encode(digest('CSE2029','sha256'),'hex')),
('a1000000-0000-0000-0000-000000000005','Arun Kumar','arun.maintenance@campus.example','worker',encode(digest('WORKER2026','sha256'),'hex'))
on conflict (id) do nothing;

insert into public.rooms (id,room_number,room_name,category,floor,capacity,benches,occupied_seats,projector,board,internet,other_resources,status) values
('b1000000-0000-0000-0000-000000000001','CSE-101','Programming Classroom','Classroom','Ground Floor',60,30,42,'Available','Whiteboard','Available','Air conditioning','Available'),
('b1000000-0000-0000-0000-000000000002','CSE-102','Smart Lecture Hall','Classroom','Ground Floor',100,50,70,'Available','Smart Board','Available','Air conditioning, audio system','Available'),
('b1000000-0000-0000-0000-000000000003','CSE-103','Data Structures Lab','Laboratory','First Floor',60,30,60,'Unavailable','Whiteboard','Available','60 desktop computers','Attention'),
('b1000000-0000-0000-0000-000000000004','CSE-104','Programming Laboratory','Laboratory','First Floor',72,36,50,'Available','Whiteboard','Available','72 desktop computers, UPS','Available'),
('b1000000-0000-0000-0000-000000000005','CSE-105','AI and Data Science Lab','Laboratory','Second Floor',65,32,38,'Available','Smart Board','Available','GPU workstations, server rack','Available'),
('b1000000-0000-0000-0000-000000000006','CSE-106','Networks Laboratory','Laboratory','Second Floor',48,24,24,'Available','Whiteboard','Available','Network racks, servers','Available'),
('b1000000-0000-0000-0000-000000000007','CSE-107','HOD Office','HOD Room','Second Floor',8,4,3,'Not applicable','Whiteboard','Available','Meeting display','Available'),
('b1000000-0000-0000-0000-000000000008','CSE-108','Seminar Hall','Seminar Hall','Second Floor',100,50,99,'Available','Smart Board','Unavailable','Air conditioning, audio system','Attention'),
('b1000000-0000-0000-0000-000000000009','CSE-109','Faculty Collaboration Room','Faculty Room','First Floor',24,12,12,'Available','Whiteboard','Available','Video conferencing','Available'),
('b1000000-0000-0000-0000-000000000010','CSE-110','Department Store','Other','Ground Floor',0,0,0,'Not applicable','Not applicable','Not applicable','Inventory shelves','Empty'),
('b1000000-0000-0000-0000-000000000011','CSE-T01','Gents Toilet','Toilet','Ground Floor',0,0,0,'Not applicable','Not applicable','Not applicable','Sanitation facilities','Available'),
('b1000000-0000-0000-0000-000000000012','CSE-T02','Ladies Toilet','Toilet','First Floor',0,0,0,'Not applicable','Not applicable','Not applicable','Sanitation facilities','Available')
on conflict (id) do nothing;

insert into public.subjects (id,code,name,semester,credits,course_category,syllabus_units,faculty_id) values
('c1000000-0000-0000-0000-000000000001','CSUC103','Fundamentals of Computer Organization',1,4,'Professional Core',5,'a1000000-0000-0000-0000-000000000001'),
('c1000000-0000-0000-0000-000000000002','CSUC101','Programming for Problem Solving',1,2,'Engineering Science',5,'a1000000-0000-0000-0000-000000000002'),
('c1000000-0000-0000-0000-000000000003','MAUC101','Mathematics I',1,4,'Basic Science',5,'a1000000-0000-0000-0000-000000000003'),
('c1000000-0000-0000-0000-000000000004','CS301','Data Structures',3,4,'Professional Core',5,'a1000000-0000-0000-0000-000000000002'),
('c1000000-0000-0000-0000-000000000005','CS302','Database Management Systems',3,4,'Professional Core',5,'a1000000-0000-0000-0000-000000000004'),
('c1000000-0000-0000-0000-000000000006','CS303','Computer Networks',3,3,'Professional Core',5,'a1000000-0000-0000-0000-000000000003'),
('c1000000-0000-0000-0000-000000000007','CS401','Artificial Intelligence',4,4,'Professional Core',5,'a1000000-0000-0000-0000-000000000001')
on conflict (id) do nothing;

insert into public.timetable (day,day_order,start_time,end_time,room_id,section,subject_id,faculty_id) values
('Monday',1,'09:00','09:50','b1000000-0000-0000-0000-000000000001','CSE-A','c1000000-0000-0000-0000-000000000004','a1000000-0000-0000-0000-000000000002'),
('Monday',1,'09:50','10:40','b1000000-0000-0000-0000-000000000004','CSE-A','c1000000-0000-0000-0000-000000000005','a1000000-0000-0000-0000-000000000004'),
('Tuesday',2,'10:50','11:40','b1000000-0000-0000-0000-000000000005','CSE-B','c1000000-0000-0000-0000-000000000007','a1000000-0000-0000-0000-000000000001'),
('Wednesday',3,'11:40','12:30','b1000000-0000-0000-0000-000000000006','CSE-B','c1000000-0000-0000-0000-000000000006','a1000000-0000-0000-0000-000000000003'),
('Thursday',4,'13:30','14:20','b1000000-0000-0000-0000-000000000003','CS1-A','c1000000-0000-0000-0000-000000000002','a1000000-0000-0000-0000-000000000002'),
('Friday',5,'14:20','15:10','b1000000-0000-0000-0000-000000000001','CS1-A','c1000000-0000-0000-0000-000000000001','a1000000-0000-0000-0000-000000000001')
on conflict do nothing;

insert into public.issues (room_id,title,category,priority,priority_rank,description,status,reported_by,assigned_to,worker_note,faculty_verification) values
('b1000000-0000-0000-0000-000000000003','Projector has no display','Projector','Critical',4,'The projector powers on but does not produce an image during scheduled laboratory sessions.','In Progress','a1000000-0000-0000-0000-000000000002','a1000000-0000-0000-0000-000000000005','Lamp assembly inspection is in progress.','Pending'),
('b1000000-0000-0000-0000-000000000008','Network connection unavailable','Network','High',3,'The seminar hall network is not reachable for scheduled presentations.','Open','a1000000-0000-0000-0000-000000000001',null,'','Pending'),
('b1000000-0000-0000-0000-000000000011','Wash basin tap leak','Sanitation','Medium',2,'A slow water leak is visible at the wash basin.','Resolved','a1000000-0000-0000-0000-000000000003','a1000000-0000-0000-0000-000000000005','Washer replaced; awaiting faculty verification.','Pending')
on conflict do nothing;

insert into public.syllabus_progress (subject_id,week_number,coverage_percent,topics_covered,updated_by) values
('c1000000-0000-0000-0000-000000000004',8,72,'Arrays, linked lists, stacks and queues completed.','a1000000-0000-0000-0000-000000000002'),
('c1000000-0000-0000-0000-000000000005',8,61,'ER modelling, relational algebra and SQL foundations completed.','a1000000-0000-0000-0000-000000000004'),
('c1000000-0000-0000-0000-000000000006',8,80,'Network models, physical layer and data link layer completed.','a1000000-0000-0000-0000-000000000003'),
('c1000000-0000-0000-0000-000000000007',8,48,'Intelligent agents and uninformed search completed.','a1000000-0000-0000-0000-000000000001'),
('c1000000-0000-0000-0000-000000000001',8,55,'Number systems, Boolean algebra and processor basics completed.','a1000000-0000-0000-0000-000000000001'),
('c1000000-0000-0000-0000-000000000002',8,68,'Problem decomposition, algorithms and C programming fundamentals completed.','a1000000-0000-0000-0000-000000000002')
on conflict (subject_id, week_number) do update set coverage_percent=excluded.coverage_percent, topics_covered=excluded.topics_covered, updated_by=excluded.updated_by, updated_at=now();
