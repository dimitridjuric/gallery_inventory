--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY "user" (name, id, email, picture) FROM stdin;
dimitri djuric	1	dimitri.djuric@gmail.com	https://lh3.googleusercontent.com/-aFyyQo75qyE/AAAAAAAAAAI/AAAAAAAAAJY/j6AGwXTSt_U/photo.jpg
User X	2	userx@xyz.com	\N
\.


--
-- Data for Name: galleries; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY galleries (name, id, address, times, url, user_id) FROM stdin;
Saatchi Gallery	1	Duke Of York's HQ, King's Road, London SW3 4RY	10am-6pm, everyday	http://www.saatchigallery.com/	1
The National Gallery	3	Trafalgar Square, London,  WC2N 5DN	Daily 10am – 6pm, Friday 10am – 9pm	http://www.nationalgallery.org.uk/	1
Tate Britain	4	Tate Britain Millbank London SW1P 4RG United Kingdom	10.00–18.00 daily	http://www.tate.org.uk/visit/tate-britain/	1
Tate Modern	2	Bankside	9 to 5	http://www.tate.org.uk/visit/tate-modern	2
\.


--
-- Name: galleries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('galleries_id_seq', 4, true);


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY inventory (title, artist, id, date, dimensions, medium, ondisplay, imgurl, gallery_id) FROM stdin;
Everything Must Go	Jean-François Boclé	1	2014		97,000 Blue plastic bags			1
The Amazement of the Gods (?)	Hans von Aachen	2	probably 1590s	35.5 x 45.8 cm	Oil on copper	Room 4		3
Giovanna Baccelli	Thomas Gainsborough	3	Exhibited 1782	Support: 2267 x 1486 mm frame: 2810 x 1830 x 155 mm	Oil paint on canvas	Room 1780		4
The Watering Place	Thomas Gainsborough	4	before 1777	147.3 x 180.3 cm	Oil on canvas	Room 34		3
Black Bean	Andy Warhol	5	1968	Support: 892 x 591 mm frame: 900 x 596 x 35 mm	Screenprint on paper	Not on display	\N	2
\.


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('inventory_id_seq', 5, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('user_id_seq', 2, true);


--
-- PostgreSQL database dump complete
--

