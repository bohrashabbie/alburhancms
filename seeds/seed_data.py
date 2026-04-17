"""
Seed script to migrate all static content from the Next.js frontend
into the PostgreSQL database via the FastAPI backend.

Run: python -m seeds.seed_data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import *
from app.utils.auth import get_password_hash


def seed_all():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # ====================================================================
        # ADMIN USER
        # ====================================================================
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                email="admin@alburhan-regional.com",
                password_hash=get_password_hash("admin123"),
                full_name="Administrator",
                role="admin",
            ))
            print("[+] Admin user created (admin / admin123)")

        # ====================================================================
        # SITE SETTINGS
        # ====================================================================
        settings_data = [
            ("company_name", "Al-Burhan Group", "مجموعة البرهان", "text", "Company name"),
            ("all_rights_reserved", "All rights reserved", "جميع الحقوق محفوظة", "text", "Copyright text"),
            ("logo_url", "/logo/AL BURHAN GROUP .png", "/logo/AL BURHAN GROUP .png", "image", "Main logo URL"),
            ("meta_title", "Al-Burhan Group - Lighting Solutions", "مجموعة البرهان - حلول الإضاءة", "text", "SEO meta title"),
            ("footer_description", "Leading lighting solutions provider delivering innovative and exceptional lighting services across the region.", "مزود رائد لحلول الإضاءة يقدم خدمات إضاءة مبتكرة واستثنائية في جميع أنحاء المنطقة.", "text", "Footer description"),
            ("footer_copyright", "All rights reserved", "جميع الحقوق محفوظة", "text", "Footer copyright"),
        ]
        for key, val_en, val_ar, stype, desc in settings_data:
            if not db.query(SiteSetting).filter(SiteSetting.key == key).first():
                db.add(SiteSetting(key=key, value_en=val_en, value_ar=val_ar, setting_type=stype, description=desc))
        print("[+] Site settings seeded")

        # ====================================================================
        # NAVIGATION ITEMS
        # ====================================================================
        nav_items = [
            ("Home", "الرئيسية", "/", "home", 1),
            ("About Us", "من نحن", "/about", "info", 2),
            ("Our Products", "منتجاتنا", "/#products", "inventory", 3),
            ("Our Projects", "مشاريعنا", "/#projects", "work", 4),
            ("Services", "الخدمات", "/#services", "build", 5),
            ("Contact", "اتصل بنا", "/contact", "phone", 6),
        ]
        if db.query(NavigationItem).count() == 0:
            for label_en, label_ar, href, icon, order in nav_items:
                db.add(NavigationItem(label_en=label_en, label_ar=label_ar, href=href, icon=icon, sort_order=order))
            print("[+] Navigation items seeded")

        # ====================================================================
        # CAROUSEL SLIDES
        # ====================================================================
        slides = [
            ("Al-Burhan Group", "مجموعة البرهان ", "Light Up Your Life", "إجعل حياتك أكثر إشراقًا ",
             "Transforming spaces with innovative lighting solutions that blend elegance, functionality, and cutting-edge technology to create breathtaking environments.",
             "نحوّل المساحات إلى تحف مضيئة عبر حلول إضاءة مبتكرة تمزج بين الأناقة  وأحدث التقنيات، لنصنع بيئات تنبض بالجمال والإبداع."),
            ("Innovation", "الابتكار", "Leading Lighting Solutions", "حلول الإضاءة الرائدة",
             "Pioneering the future of illumination with state-of-the-art LED technology, smart lighting systems, and energy-efficient designs that redefine modern living.",
             "نرسم مستقبل الإضاءة بتقنيات LED الحديثة، وأنظمة الإضاءة الذكية، والتصاميم الموفّرة للطاقة، لنقدّم تجربة عيش عصرية تجمع بين الأناقة والكفاءة."),
            ("Excellence", "التميز", "Premium Quality Products", "منتجات عالية الجودة",
             "Crafted with precision and passion, our premium lighting collections combine exceptional craftsmanship with luxurious materials to elevate any space.",
             "صُنعت مجموعات الإضاءة الفاخرة لدينا بدقة وشغف، وتجمع بين الحرفية الاستثنائية والمواد الفاخرة لتُضفي لمسةً مميزة على أي مساحة."),
            ("Design", "التصميم", "Elegant Lighting Designs", "تصاميم اضاءة أنيقة ",
             "Where artistry meets functionality. Our curated designs seamlessly integrate aesthetic beauty with practical innovation, creating timeless pieces that inspire.",
             "حيث تلتقي البراعة الفنية بالتطبيق العملي. تتكامل تصاميمنا المختارة بعناية مع الجمال الجمالي والابتكار العملي، فنبتكر قطعًا خالدة ملهمة."),
            ("Experience", "الخبرة", "20+ Years of Expertise", "اكثر من ٢٠ سنه من الخبرة",
             "Drawing from over two decades of industry excellence, we deliver unmatched expertise in lighting design, installation, and project implementation across the globe.",
             "بفضل خبرتنا الممتدة لأكثر من عقدين من التميز في الاضاءة، فإننا نقدم خبرة لا مثيل لها في تصميم الإضاءة وتركيبها وتنفيذ المشاريع في جميع أنحاء العالم."),
            ("Quality", "الجودة", "Exceptional Craftsmanship", "حرفية استثنائية",
             "Every fixture is meticulously engineered and quality-assured, ensuring durability, performance, and lasting beauty that exceeds the highest international standards.",
             " كل تركيبات الإضاءة لدينا تم تصميمها بعناية فائقة مما يضمن الجودة والمتانة والأداء والجمال الدائم الذي يتجاوز أعلى المعايير الدولية."),
            ("Vision", "رؤيتنا", "Illuminating Your Future", "نضيء مستقبلك",
             "Embracing tomorrow's possibilities today. We envision a world where intelligent lighting transforms how we live, work, and experience our surroundings.",
             "نحتضن اليوم إمكانيات الغد. نتخيل عالمًا تُغيّر فيه الإضاءة الذكية أسلوب حياتنا وعملنا وتجاربنا مع بيئتنا."),
        ]
        if db.query(CarouselSlide).count() == 0:
            for i, (t_en, t_ar, s_en, s_ar, d_en, d_ar) in enumerate(slides):
                db.add(CarouselSlide(
                    title_en=t_en, title_ar=t_ar, subtitle_en=s_en, subtitle_ar=s_ar,
                    description_en=d_en, description_ar=d_ar, sort_order=i + 1,
                ))
            print("[+] Carousel slides seeded")

        # ====================================================================
        # PAGE CONTENTS
        # ====================================================================
        page_contents = [
            # Hero
            ("home", "hero_title1", "Illuminating", "إضاءة", None, None),
            ("home", "hero_title2", "Your Vision", "رؤيتك", None, None),
            ("home", "hero_title3", "Beyond Light", "أبعد من الضوء", None, None),
            ("home", "hero_description", None, None,
             "Transforming spaces with innovative lighting solutions that combine aesthetics, functionality, and sustainability.",
             "تحويل المساحات بحلول إضاءة مبتكرة تجمع بين الجمال والوظائف والاستدامة."),
            # Section headings
            ("home", "section_aboutUs", "Our Global Companies", "شركاتنا العالمية", None, None),
            ("home", "section_aboutUsTitle", "About Us", "من نحن", None, None),
            ("home", "section_introduction", "Introduction", "مقدمة", None, None),
            ("home", "section_fromOwner", "A Word from the Founder", "كلمة من المؤسس", None, None),
            ("home", "section_ourBrand", "Our Brands", "علامتنا التجارية", None, None),
            ("home", "section_europeanBrands", "Our Partnership Brands", "شركاؤنا من العلامات التجارية الموثوقة", None, None),
            ("home", "section_ourProjects", "Our Projects", "مشاريعنا", None, None),
            ("home", "section_ourProduct", "Our Product", "منتجاتنا", None, None),
            ("home", "section_contactUs", "Contact Us", "اتصل بنا", None, None),
            # Introduction section
            ("home", "introduction_description", None, None,
             "Al-Burhan Group is a leading provider of innovative lighting solutions with over 20 years of industry experience. We combine quality, expertise, and customer satisfaction to deliver exceptional lighting services across the region.",
             "شركة مجموعة البرهان هي شركة رائدة في تقديم حلول الإضاءة المبتكرة، تتمتع بخبرة تزيد عن 20 عامًا في هذا المجال. نحن نجمع بين الجودة والخبرة ورضا العملاء لنقدّم خدمات إضاءة استثنائية في مختلف أنحاء الم"),
            ("home", "introduction_additionalInfo", None, None,
             "With hundreds of successful projects worldwide, including in China, Kuwait, UAE, and Egypt, Al-Burhan Group has established itself as a trusted name in lighting.",
             "من خلال تنفيذ مئات المشاريع الناجحة حول العالم  بما في ذلك في الصين والكويت والإمارات ومصر أثبتت البرهان نفسها كاسم موثوق في عالم الإضاءة."),
            ("home", "introduction_thirdParagraph", None, None,
             "From cutting-edge LED technologies to elegant designer collections, we transform visions into reality, creating inspiring lighting experiences that elevate every space.",
             "ومن خلال أحدث تقنيات الإضاءة بتقنية الـ LED والمجموعات التصميمية الراقية، نحول الرؤى إلى واقع، ونصنع تجارب إضاءة ملهمة ترفع من قيمة وجمال كل مساحة."),
            # About page
            ("about", "title", "About Us", "من نحن", None, None),
            ("about", "mainDescription", None, None,
             "With more than 20 years of experience in the lighting industry, Al Burhan Regional has successfully established itself as one of the leading providers of comprehensive lighting solutions in the State of Kuwait. Our commitment to quality, innovation, and professional service has enabled us to deliver reliable lighting solutions for residential, commercial, governmental, and industrial projects.",
             "مع أكثر من 20 عامًا من الخبرة في صناعة الإضاءة، نجحت البرهان الإقليمية في ترسيخ نفسها كواحدة من المزودين الرائدين لحلول الإضاءة الشاملة في دولة الكويت. التزامنا بالجودة والابتكار والخدمة المهنية مكننا من تقديم حلول إضاءة موثوقة للمشاريع السكنية والتجارية والحكومية والصناعية."),
            ("about", "journey", None, None,
             "Our journey began in Kuwait, where we built our foundation and reputation in the lighting market. As our expertise grew and demand for our services increased, we expanded our operations regionally and internationally. Today, Al Burhan Regional Lighting proudly operates branches in:",
             "بدأت رحلتنا في الكويت، حيث بنينا أساسنا وسمعتنا في سوق الإضاءة. مع نمو خبرتنا وزيادة الطلب على خدماتنا، وسعنا عملياتنا إقليميًا ودوليًا. اليوم، تعمل البرهان الإقليمية للإضاءة بفخر من خلال فروعها في:"),
            ("about", "expansion", None, None,
             "This expansion reflects our vision of becoming a regional leader capable of delivering advanced lighting solutions across the Middle East and beyond. We have become the Burhan Group, which includes a group of companies around the world.",
             "يعكس هذا التوسع رؤيتنا في أن نصبح قائدًا إقليميًا قادرًا على تقديم حلول إضاءة متقدمة عبر الشرق الأوسط وما بعده. لقد أصبحنا مجموعة البرهان، والتي تضم مجموعة البرهان الشركات حول العالم."),
            ("about", "whatWeOffer_title", "What We Offer", "ما نقدمه", None, None),
            ("about", "whatWeOffer_description", None, None,
             "We provide a fully integrated range of lighting services:",
             "نوفر مجموعة متكاملة بالكامل من خدمات الإضاءة:"),
            ("about", "sectorsWeServe_title", "Sectors We Serve", "القطاعات التي نخدمها", None, None),
            ("about", "sectorsWeServe_description", None, None,
             "We cover a wide range of project sectors, including:",
             "نغطي مجموعة واسعة من قطاعات المشاريع، بما في ذلك:"),
            ("about", "sectorsWeServe_closing", None, None,
             "Whether it is a private villa, office building, retail shop, restaurant, or governmental facility, we provide the most suitable lighting solutions based on project requirements and budget.",
             "سواء كانت فيلا خاصة، أو مبنى مكتبي، أو متجر تجاري، أو مطعم، أو منشأة حكومية، فإننا نقدم حلول الإضاءة الأنسب بناءً على متطلبات المشروع والميزانية."),
            ("about", "vision", "Our Vision", "رؤيتنا",
             "To be the top provider of advanced lighting solutions in Kuwait and the regional market, offering modern, efficient, and high-quality products that enhance both functionality and aesthetics.",
             "أن نكون المزود الرائد لحلول الإضاءة المتقدمة في الكويت والسوق الإقليمي، ونقدم منتجات حديثة وفعالة وعالية الجودة تعزز كلًا من الوظائف والجماليات."),
            ("about", "mission", "Our Mission", "مهمتنا",
             "To deliver complete lighting solutions through:",
             "تقديم حلول إضاءة كاملة من خلال:"),
            ("about", "mission_item1", "High-quality products", "منتجات عالية الجودة", None, None),
            ("about", "mission_item2", "Professional design", "تصميم احترافي", None, None),
            ("about", "mission_item3", "Precise execution", "تنفيذ دقيق", None, None),
            ("about", "mission_item4", "On-time delivery", "تسليم في الوقت المحدد", None, None),
            # Contact page
            ("contact", "title", "Contact Us", "اتصل بنا", None, None),
            ("contact", "subtitle", None, None,
             "Get in touch with our offices around the world",
             "تواصل مع مكاتبنا حول العالم"),
            ("contact", "selectCountry", None, None,
             "Select a country to view contact details",
             "اختر دولة لعرض تفاصيل الاتصال"),
            ("contact", "viewDetails", "View Contact Details", "عرض تفاصيل الاتصال", None, None),
            # Contact form labels
            ("contact", "form_name", "Name", "الاسم", None, None),
            ("contact", "form_email", "Email", "البريد الإلكتروني", None, None),
            ("contact", "form_phone", "Phone", "الهاتف", None, None),
            ("contact", "form_subject", "Subject", "الموضوع", None, None),
            ("contact", "form_message", "Message", "الرسالة", None, None),
            ("contact", "form_sendMessage", "Send Message", "إرسال الرسالة", None, None),
            ("contact", "headOffice", "Head Office", "المكتب الرئيسي", None, None),
            ("contact", "ourLocation", "Our Location", "موقعنا", None, None),
            ("contact", "ourLocations", "Our Locations", "مواقعنا", None, None),
            ("contact", "address_label", "Address", "العنوان", None, None),
            ("contact", "phoneNumbers", "Phone Numbers", "أرقام الهاتف", None, None),
            ("contact", "email_label", "Email", "البريد الإلكتروني", None, None),
            ("contact", "businessHours", "Business Hours", "ساعات العمل", None, None),
            ("contact", "hours", "Sat-Thu: 9:00 AM - 7:00 PM, Friday: Closed", "السبت - الخميس: 9:00 صباحاً - 7:00 مساءً، الجمعة: مغلق", None, None),
        ]
        if db.query(PageContent).count() == 0:
            for i, (pk, sk, t_en, t_ar, c_en, c_ar) in enumerate(page_contents):
                db.add(PageContent(
                    page_key=pk, section_key=sk,
                    title_en=t_en, title_ar=t_ar,
                    content_en=c_en, content_ar=c_ar,
                    sort_order=i + 1,
                ))
            print("[+] Page contents seeded")

        # ====================================================================
        # SERVICES (What We Offer)
        # ====================================================================
        if db.query(Service).count() == 0:
            services_data = [
                ("Lighting Design", "تصميم الإضاءة", "/Our Service/designing.png", "DesignServices", [
                    ("Project assessment and concept development", "تقييم المشروع وتطوير المفهوم"),
                    ("Interior and exterior lighting layouts", "تخطيطات الإضاءة الداخلية والخارجية"),
                    ("Fixture selection tailored to architectural and decorative needs", "اختيار التركيبات المصممة خصيصًا للاحتياجات المعمارية والديكورية"),
                ]),
                ("Lighting Supply", "توريد الإضاءة", "/Our Service/supply.png", "Inventory", [
                    ("A wide range of high-quality indoor and outdoor lighting products", "مجموعة واسعة من منتجات الإضاءة الداخلية والخارجية عالية الجودة"),
                    ("Downlights, spotlights, LED strips, linear lighting, decorative fixtures, façade lighting, and more", "الأنوار المدمجة، والأنوار الموجهة، وشرائط LED، والإضاءة الخطية، والتركيبات الزخرفية، وإضاءة الواجهات، والمزيد"),
                    ("Products selected from trusted global brands", "منتجات مختارة من علامات تجارية عالمية موثوقة"),
                ]),
                ("Supply & Install (Turnkey Solutions)", "التوريد والتركيب (حلول متكاملة)", "/Our Service/installation.png", "Build", [
                    ("Complete project execution", "تنفيذ المشروع الكامل"),
                    ("Specialized installation teams", "فرق تركيب متخصصة"),
                    ("On-site coordination with contractors and consultants to ensure optimal results", "التنسيق في الموقع مع المقاولين والاستشاريين لضمان النتائج المثلى"),
                ]),
                ("After-Sales Support", "دعم ما بعد البيع", "/Our Service/after sales service.png", "Support", [
                    ("Post-installation follow-up", "المتابعة بعد التركيب"),
                    ("Technical support and maintenance", "الدعم الفني والصيانة"),
                    ("Alternative solutions for future upgrades or modifications", "حلول بديلة للترقيات أو التعديلات المستقبلية"),
                ]),
            ]
            for i, (t_en, t_ar, img, icon, items) in enumerate(services_data):
                svc = Service(title_en=t_en, title_ar=t_ar, image_url=img, icon=icon, sort_order=i + 1)
                db.add(svc)
                db.flush()
                for j, (it_en, it_ar) in enumerate(items):
                    db.add(ServiceItem(service_id=svc.id, text_en=it_en, text_ar=it_ar, sort_order=j + 1))
            print("[+] Services seeded")

        # ====================================================================
        # SECTORS
        # ====================================================================
        if db.query(Sector).count() == 0:
            sectors_data = [
                ("Government Projects", "المشاريع الحكومية", "AccountBalance"),
                ("Private Sector", "القطاع الخاص", "Business"),
                ("Commercial Developments", "التطويرات التجارية", "Business"),
                ("Retail Stores", "المتاجر التجارية", "Store"),
                ("Residential Villas & Apartments", "الفلل والشقق السكنية", "Home"),
                ("Industrial Warehouses and Facilities", "المستودعات والمرافق الصناعية", "Factory"),
            ]
            for i, (n_en, n_ar, icon) in enumerate(sectors_data):
                db.add(Sector(name_en=n_en, name_ar=n_ar, icon=icon, sort_order=i + 1))
            print("[+] Sectors seeded")

        # ====================================================================
        # TEAM MEMBERS (Owners)
        # ====================================================================
        if db.query(TeamMember).count() == 0:
            db.add(TeamMember(
                name_en="Mr. Murtaza Bohra", name_ar="السيد مرتضى بوهرا",
                designation_en="Founder", designation_ar="المؤسس",
                quote_en="Twenty years ago, all I had was a small dream to bring something different to the world of lighting.\n\nWe started with humble steps, and over time that dream grew. Today, it has become a name we are proud of Al Burhan Group.\n\nEvery achievement we've made is the result of hard work, dedication, and belief that success comes from honesty and persistence.\n\nI'm proud of everyone who has been part of this journey, and of every light we've brought into people's lives.\n\nOur journey is far from over. Every new project is a new beginning, a new dream to shine brighter.",
                quote_ar="قبل عشرين عامًا، كل ما كان لدي كان حلمًا صغيرًا لجلب شيء مختلف إلى عالم الإضاءة.\n\nبدأنا بخطوات متواضعة، ومع مرور الوقت نما ذلك الحلم. اليوم، أصبح اسماً نفخر به مجموعة البرهان للإضاءة.\n\nكل إنجاز حققناه هو نتيجة العمل الجاد والتفاني والاعتقاد بأن النجاح يأتي من الصدق والمثابرة.\n\nأفتخر بكل من كان جزءًا من هذه الرحلة، وبكل ضوء جلبناه إلى حياة الناس.\n\nرحلتنا لم تنته بعد. كل مشروع جديد هو بداية جديدة، حلم جديد للتألق بشكل أكثر إشراقًا.",
                sort_order=1,
            ))
            db.add(TeamMember(
                name_en="Mr. Shabbir Hussain", name_ar="السيد شبير رطلاموالا",
                designation_en="Co-founder", designation_ar="الشريك المؤسس",
                quote_en="It all began with a simple idea to create lighting that inspires and beautifies every space.\n\nToday, that dream has become a reality under the name Al Burhan Group, where quality and creativity are at the heart of every project.\n\nThe journey has been full of challenges, but it has taught us that determination, hard work, and a belief in innovation make all the difference.\n\nI am proud of everyone who has been part of this journey, and of every light we have shared to bring warmth and beauty into people's lives.\n\nBecause we still believe in the dream, every new step is an opportunity to shine even brighter and turn ideas into radiant realities.",
                quote_ar="كل شيء بدأ بفكرة بسيطة لإنشاء إضاءة تلهم وتجمّل كل مساحة.\n\nاليوم، أصبح ذلك الحلم حقيقة تحت اسم مجموعة البرهان  حيث الجودة والإبداع في قلب كل مشروع.\n\nكانت الرحلة مليئة بالتحديات، لكنها علمتنا أن التصميم والعمل الجاد والإيمان بالابتكار يحدثان كل الفرق.\n\nأفتخر بكل من كان جزءًا من هذه الرحلة، وبكل ضوء شاركناه لجلب الدفء والجمال إلى حياة الناس.\n\nلأننا لا نزال نؤمن بالحلم، كل خطوة جديدة هي فرصة للتألق بشكل أكثر إشراقًا وتحويل الأفكار إلى حقائق مشعة.",
                sort_order=2,
            ))
            print("[+] Team members seeded")

        # ====================================================================
        # COUNTRIES
        # ====================================================================
        if db.query(Country).count() == 0:
            countries_data = [
                ("Kuwait", "الكويت", "kuwait", "Al-Burhan Regional", "البرهان الإقليمية",
                 "Al-Burhan Regional has been a cornerstone of the lighting industry in Kuwait for over two decades. Our extensive network of branches across the country ensures accessibility and exceptional service to clients throughout the region, from residential to commercial projects.",
                 "كان البرهان الإقليمي حجر الزاوية في صناعة الإضاءة في الكويت لأكثر من عقدين. تضمن شبكة فروعنا الواسعة في جميع أنحاء البلاد إمكانية الوصول والخدمة الاستثنائية للعملاء في جميع أنحاء المنطقة، من المشاريع السكنية إلى التجارية.",
                 "https://flagcdn.com/w320/kw.png", "/Countries/kuwait.png", "/logo/al burhan kuwait.png", 1),
                ("United Arab Emirates", "الإمارات العربية المتحدة", "uae", "Al-Burhan Hegazi", "البرهان حجازي",
                 "In the heart of Dubai, Al-Burhan Hegazi serves as our gateway to the dynamic Middle Eastern market. We bring innovative lighting solutions to one of the world's most ambitious architectural landscapes, contributing to iconic projects that define modern luxury and sophistication.",
                 "في قلب دبي، يخدم البرهان حجازي كبوابة لنا إلى السوق الشرقي الأوسطي الديناميكي. نجلب حلول إضاءة مبتكرة إلى أحد أكثر المشاريع المعمارية طموحًا في العالم، نساهم في مشاريع أيقونية تحدد الفخامة والأناقة الحديثة.",
                 "https://flagcdn.com/w320/ae.png", "/Company Countries/dubai city.jpg", "/logo/AL BURHAN UAE.png", 2),
                ("China", "الصين", "china", "Al-Bohan", "AL-Bohan",
                 "Al-Burhan's presence in China represents our commitment to manufacturing excellence and innovation. Through our strategic partnerships and state-of-the-art facilities, we deliver world-class lighting solutions that combine quality craftsmanship with cutting-edge technology, serving markets across the globe.",
                 "يمثل وجود البرهان في الصين التزامنا بالتميز في التصنيع والابتكار. من خلال شراكاتنا الاستراتيجية ومرافقنا الحديثة، نقدم حلول إضاءة عالمية المستوى تجمع بين الحرفية المتميزة والتكنولوجيا المتطورة، لخدمة الأسواق في جميع أنحاء العالم.",
                 "https://flagcdn.com/w320/cn.png", None, None, 3),
                ("Egypt", "مصر", "egypt", "Al-Burhan", "البرهان حجازي",
                 None, None,
                 "https://flagcdn.com/w320/eg.png", None, None, 4),
            ]
            for n_en, n_ar, slug, fn_en, fn_ar, d_en, d_ar, flag, img, logo, order in countries_data:
                db.add(Country(
                    name_en=n_en, name_ar=n_ar, slug=slug,
                    firm_name_en=fn_en, firm_name_ar=fn_ar,
                    description_en=d_en, description_ar=d_ar,
                    flag_url=flag, country_image_url=img, logo_url=logo,
                    sort_order=order,
                ))
            print("[+] Countries seeded")

        db.flush()

        # ====================================================================
        # CONTACT INFO (per country)
        # ====================================================================
        if db.query(ContactInfo).count() == 0:
            kuwait = db.query(Country).filter(Country.slug == "kuwait").first()
            uae = db.query(Country).filter(Country.slug == "uae").first()
            china = db.query(Country).filter(Country.slug == "china").first()
            egypt = db.query(Country).filter(Country.slug == "egypt").first()

            # Head office (Kuwait)
            db.add(ContactInfo(
                country_id=kuwait.id if kuwait else None,
                company_name_en="Al-Burhan Regional", company_name_ar="البرهان الإقليمية",
                address_en="Kuwait, Hawally, Tunis Street, Al Refaei Building, 4th Floor, Office 5&6",
                address_ar="الكويت، حولي، شارع تونس، مبنى الرفاعي، الطابق الرابع، مكتب 5 و 6",
                phone1="+965 99935529", phone2="+965 22280853",
                email="Info@alburhan-regional.com",
                business_hours_en="Sat-Thu: 9:00 AM - 7:00 PM, Friday: Closed",
                business_hours_ar="السبت - الخميس: 9:00 صباحاً - 7:00 مساءً، الجمعة: مغلق",
                is_head_office=True,
            ))
            # UAE
            db.add(ContactInfo(
                country_id=uae.id if uae else None,
                company_name_en="AL BURHAN HEGAZI GENERAL TRADING LLC",
                company_name_ar="البرهان حجازي للتجارة العامة ذ.م.م",
                office_en="OFFICE #13", office_ar="المكتب رقم 13",
                floor_en="M FLOOR, AL OWAIS BUSINESS TOWER", floor_ar="الطابق M، برج العويس للأعمال",
                area_en="AL SABHKA, DEIRA", area_ar="الصبخة، ديرة",
                city_en="DUBAI, UNITED ARAB EMIRATES", city_ar="دبي، الإمارات العربية المتحدة",
                phone1="+971 56 6032 765", phone2="+971 4 5775 302",
                email="bdm@alburhan-regional.com",
            ))
            # China
            db.add(ContactInfo(
                country_id=china.id if china else None,
                company_name_en="JIANGMEN BOHAN LIGHTING CO., LTD.",
                company_name_ar="JIANGMEN BOHAN LIGHTING CO., LTD.",
                address_en="B2 BUILDING, NO. 159th, YUOIN ROAD,",
                address_ar="مبنى B2، رقم 159، طريق يوون،",
                district_en="JIANGHAI DISTRICT, JIANGMEN CITY,",
                district_ar="منطقة جيانغهاي، مدينة جيانغمن،",
                province_en="GUANGDONG PROVINCE, CHINA",
                province_ar="مقاطعة قوانغدونغ، الصين",
                postal_code="529000",
                phone1="+8613726006786",
                email="AL@ALBURHANLIGHTING.COM",
                website="www.alburhanlighting.com",
            ))
            # Egypt
            db.add(ContactInfo(
                country_id=egypt.id if egypt else None,
                company_name_en="Al-Burhan", company_name_ar="البرهان",
                address_en="Address information to be added",
                address_ar="معلومات العنوان سيتم إضافتها",
                phone1="Phone information to be added",
                email="Email information to be added",
            ))
            print("[+] Contact info seeded")

        # ====================================================================
        # BRANCHES (Kuwait branches)
        # ====================================================================
        if db.query(Branch).count() == 0:
            kuwait = db.query(Country).filter(Country.slug == "kuwait").first()
            if kuwait:
                branches_data = [
                    ("Hawally 1st branch", "فرع حولي الأول", "Tunis street in front of al rehab complex", "شارع تونس مقابل مجمع الرحاب", "66895662"),
                    ("Hawally second branch", "فرع حولي الثاني", "Tunis street Opposite Hawalli Governorate", "شارع تونس مقابل محافظة حولي", "69979153"),
                    ("Shuweikh branch", "فرع الشويخ", "electricity street", "شارع الكهرباء", "60344088"),
                    ("Jahraa branch", "فرع الجهراء", "Jahra Industrial Area", "المنطقة الصناعية بالجهراء", "66890566"),
                ]
                for i, (n_en, n_ar, a_en, a_ar, phone) in enumerate(branches_data):
                    db.add(Branch(
                        country_id=kuwait.id, name_en=n_en, name_ar=n_ar,
                        address_en=a_en, address_ar=a_ar, phone1=phone,
                        sort_order=i + 1,
                    ))
                print("[+] Branches seeded")

        # ====================================================================
        # SOCIAL LINKS
        # ====================================================================
        if db.query(SocialLink).count() == 0:
            social_data = [
                ("facebook", "https://www.facebook.com/alburhanregional", "Facebook", 1),
                ("instagram", "https://www.instagram.com/alburhanregional", "Instagram", 2),
                ("twitter", "https://twitter.com/alburhanregion", "Twitter", 3),
                ("linkedin", "https://www.linkedin.com/company/alburhanregional", "LinkedIn", 4),
            ]
            for platform, url, icon, order in social_data:
                db.add(SocialLink(platform=platform, url=url, icon=icon, sort_order=order))
            print("[+] Social links seeded")

        # ====================================================================
        # PRODUCTS
        # ====================================================================
        if db.query(Product).count() == 0:
            products_data = [
                ("Smart Lighting", "الإضاءة الذكية"),
                ("Commercial Lighting", "الإضاءة التجارية"),
                ("Industrial Lighting", "الإضاءة الصناعية"),
                ("Residential Lighting", "الإضاءة السكنية"),
            ]
            for i, (n_en, n_ar) in enumerate(products_data):
                db.add(Product(name_en=n_en, name_ar=n_ar, sort_order=i + 1))
            print("[+] Products seeded")

        # ====================================================================
        # FOOTER LINKS
        # ====================================================================
        if db.query(FooterLink).count() == 0:
            footer_data = [
                ("services", "Interior Lighting", "إضاءة داخلية", "#", 1),
                ("services", "Commercial Lighting", "إضاءة تجارية", "#", 2),
                ("services", "Exterior Lighting", "إضاءة خارجية", "#", 3),
                ("services", "Smart Lighting", "إضاءة ذكية", "#", 4),
                ("services", "Lighting Design", "تصميم الإضاءة", "#", 5),
                ("services", "Installation Services", "خدمات التركيب", "#", 6),
                ("legal", "Privacy Policy", "سياسة الخصوصية", "/privacy", 1),
                ("legal", "Terms of Service", "شروط الخدمة", "/terms", 2),
                ("legal", "Cookie Policy", "سياسة ملفات تعريف الارتباط", "/cookies", 3),
                ("legal", "GDPR", "GDPR", "/gdpr", 4),
            ]
            for section, l_en, l_ar, href, order in footer_data:
                db.add(FooterLink(section=section, label_en=l_en, label_ar=l_ar, href=href, sort_order=order))
            print("[+] Footer links seeded")

        # ====================================================================
        # PROJECT CATEGORIES & PROJECTS (Static fallback data)
        # ====================================================================
        if db.query(ProjectCategory).count() == 0:
            categories = {
                "Gyms": ("صالات رياضية", [
                    ("Oxygen Gym Jahra", ["/OurProject/Oxygen Gym Jahra/IMG-20251130-WA0005.jpg", "/OurProject/Oxygen Gym Jahra/IMG-20251130-WA0008.jpg", "/OurProject/Oxygen Gym Jahra/IMG-20251130-WA0011.jpg", "/OurProject/Oxygen Gym Jahra/IMG-20251130-WA0012.jpg"]),
                    ("Oxygen Gym KSA", ["/OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.06 PM.jpeg", "/OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.11 PM..jpeg"]),
                    ("Oxygen Gym Mahboula", ["/OurProject/Oxygen Gym Mahboula/WhatsApp Image 2025-12-09 at 8.32.33 PM.jpeg", "/OurProject/Oxygen Gym Mahboula/WhatsApp Image 2025-12-09 at 8.33.30 PM.jpeg"]),
                    ("Oxygen Gym UAE", ["/OurProject/Oxygen Gym U.A.E/WhatsApp Image 2025-12-09 at 8.33.39 PM.jpeg", "/OurProject/Oxygen Gym U.A.E/WhatsApp Image 2025-12-09 at 8.33.43 PM.jpeg"]),
                    ("Peak Gym Qurain", ["/OurProject/Peak Gym Qurain/WhatsApp Image 2025-12-09 at 8.40.13 PM (1).jpeg", "/OurProject/Peak Gym Qurain/WhatsApp Image 2025-12-09 at 8.40.13 PM.jpeg"]),
                    ("Plage Gym", ["/OurProject/Plage Gym/WhatsApp Image 2026-01-02 at 3.38.06 PM.jpeg"]),
                ]),
                "Restaurants": ("مطاعم", [
                    ("Nandos Al Kout Mall", ["/OurProject/Nandos Al Kout Mall/Nandos Al Kout Mall/12.jpg", "/OurProject/Nandos Al Kout Mall/Nandos Al Kout Mall/14.jpg"]),
                    ("Wing Stop Al Bida", ["/OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.32 AM (1).jpeg"]),
                    ("Wing Stop Salmiya", ["/OurProject/Wing Stop Salmiya/Wing Stop Salmiya/WhatsApp Image 2025-08-23 at 11.29.56 AM (2).jpeg"]),
                    ("Paul Le Cafe", ["/OurProject/Paul Le Cafe/Paul Le Cafe/WhatsApp Image 2025-12-09 at 8.30.21 PM.jpeg"]),
                    ("Wings Stop Liwan", ["/OurProject/Wings Stop Liwan/Wings Stop Liwan/WhatsApp Image 2025-12-09 at 8.33.47 PM.jpeg"]),
                    ("Wings Stop Assima Mall", ["/OurProject/Wings Stop Assima Mall/Wings Stop Assima Mall/WhatsApp Image 2025-12-09 at 8.33.45 PM (1).jpeg"]),
                ]),
                "Showrooms": ("صالات عرض", [
                    ("Dar Al Saback", ["/OurProject/Dar Al Saback/Dar Al Saback/WhatsApp Image 2025-12-09 at 8.30.23 PM (1).jpeg"]),
                    ("Beverly Hills", ["/OurProject/Beverly Hills/Beverly Hills/WhatsApp Image 2025-08-22 at 1.49.44 PM.jpeg"]),
                    ("Audi Showroom", ["/OurProject/Audi Showroom/Audi Showroom/WhatsApp Image 2025-08-23 at 19.37.39_bf3d8686.jpg"]),
                    ("Inglot", ["/OurProject/Inglot/Inglot/WhatsApp Image 2025-08-22 at 1.40.37 PM.jpeg"]),
                    ("Dune London", ["/OurProject/Dune London/Dune London/WhatsApp Image 2025-08-22 at 1.49.46 PM.jpeg"]),
                ]),
                "Banks": ("بنوك", [
                    ("Warba Bank", ["/OurProject/Warba Bank/Warba Bank/WhatsApp Image 2025-12-09 at 8.30.27 PM.jpeg"]),
                    ("HSBC", ["/OurProject/HSBC/HSBC/WhatsApp Image 2025-12-09 at 8.30.24 PM (2).jpeg"]),
                ]),
                "Offices": ("مكاتب", [
                    ("STC Office Assima Tower", ["/OurProject/STC Office Assima Tower/STC Office Assima Tower/WhatsApp Image 2025-09-29 at 14.22.19.jpeg"]),
                    ("Zain Al Rai", ["/OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.16 PM (2).jpeg"]),
                ]),
            }
            for i, (cat_en, (cat_ar, projs)) in enumerate(categories.items()):
                cat = ProjectCategory(name_en=cat_en, name_ar=cat_ar, sort_order=i + 1)
                db.add(cat)
                db.flush()
                for j, (proj_name, images) in enumerate(projs):
                    proj = Project(category_id=cat.id, name_en=proj_name, name_ar=proj_name, sort_order=j + 1)
                    db.add(proj)
                    db.flush()
                    for k, img_url in enumerate(images):
                        db.add(ProjectImage(project_id=proj.id, image_url=img_url, sort_order=k + 1))
            print("[+] Project categories & projects seeded")

        # ====================================================================
        # STATIC PAGES
        # ====================================================================
        if db.query(StaticPage).count() == 0:
            pages = [
                ("privacy", "Privacy Policy", "سياسة الخصوصية", "Privacy policy content here.", "محتوى سياسة الخصوصية هنا."),
                ("terms", "Terms of Service", "شروط الخدمة", "Terms of service content here.", "محتوى شروط الخدمة هنا."),
                ("cookies", "Cookie Policy", "سياسة ملفات تعريف الارتباط", "Cookie policy content here.", "محتوى سياسة ملفات تعريف الارتباط هنا."),
                ("gdpr", "GDPR", "GDPR", "GDPR content here.", "محتوى GDPR هنا."),
            ]
            for slug, t_en, t_ar, c_en, c_ar in pages:
                db.add(StaticPage(slug=slug, title_en=t_en, title_ar=t_ar, content_en=c_en, content_ar=c_ar))
            print("[+] Static pages seeded")

        db.commit()
        print("\n[SUCCESS] All seed data inserted successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
