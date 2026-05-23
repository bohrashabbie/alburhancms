"""
Seed script that populates the AL-Burhan CMS database.

Physical files live in ./uploads/ (copied from the Next.js /public folder).
Every DB row stores ITS OWN image path (e.g. a Brand.logo_url = /uploads/Brands/brand4.jpg).
A MediaFile row is also created for every file on disk so the admin media library
lists every available asset and allows add/edit/delete via the existing
/api/media endpoints.

Run:   python -m seeds.seed_data
"""
import os
import sys
import mimetypes

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import *  # noqa: F401, F403
from app.utils.auth import get_password_hash
from app.config import get_settings

settings = get_settings()

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

UPLOAD_DIR = settings.UPLOAD_DIR  # "uploads"


def up(path: str) -> str:
    """Given a relative path inside uploads/, return the public URL prefix."""
    p = path.replace("\\", "/").lstrip("/")
    return f"/{UPLOAD_DIR}/{p}"


def scan_uploads() -> list[tuple[str, str, str, int]]:
    """Walk the uploads/ folder and return (rel_path, url, mime, size) for each file."""
    out = []
    if not os.path.isdir(UPLOAD_DIR):
        return out
    for root, _dirs, files in os.walk(UPLOAD_DIR):
        for name in files:
            abs_path = os.path.join(root, name)
            rel = os.path.relpath(abs_path, UPLOAD_DIR).replace("\\", "/")
            mime, _ = mimetypes.guess_type(abs_path)
            try:
                size = os.path.getsize(abs_path)
            except OSError:
                size = 0
            out.append((rel, up(rel), mime or "application/octet-stream", size))
    return out


# --------------------------------------------------------------------------
# Main seeder
# --------------------------------------------------------------------------

def seed_all():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # ==================================================================
        # ADMIN USER
        # ==================================================================
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                email="admin@alburhan-regional.com",
                password_hash=get_password_hash("admin123"),
                full_name="Administrator",
                role="admin",
            ))
            print("[+] Admin user created (admin / admin123)")

        # ==================================================================
        # MEDIA FILES  (one row per file under ./uploads/)
        # ==================================================================
        admin = db.query(User).filter(User.username == "admin").first()
        db.flush()
        admin_id = admin.id if admin else None

        scanned = scan_uploads()
        inserted = 0
        for rel, url, mime, size in scanned:
            # de-duplicate on file_path (the /uploads/... URL)
            if db.query(MediaFile).filter(MediaFile.file_path == url).first():
                continue
            filename = rel.split("/")[-1]
            db.add(MediaFile(
                filename=filename,
                original_name=filename,
                file_path=url,
                file_type=mime,
                file_size=size,
                uploaded_by=admin_id,
            ))
            inserted += 1
        if inserted:
            print(f"[+] {inserted} media files registered")
        else:
            print(f"[=] media library already in sync ({len(scanned)} files on disk)")

        # ==================================================================
        # SITE SETTINGS
        # ==================================================================
        settings_data = [
            ("company_name", "Al-Burhan Group", "مجموعة البرهان", "text", "Company name"),
            ("all_rights_reserved", "All rights reserved", "جميع الحقوق محفوظة", "text", "Copyright text"),
            ("logo_url", up("logo/AL BURHAN GROUP .png"), up("logo/AL BURHAN GROUP .png"), "image", "Main site logo"),
            ("favicon_url", up("locationpin.png"), up("locationpin.png"), "image", "Favicon (fallback)"),
            ("meta_title", "Al-Burhan Group - Lighting Solutions", "مجموعة البرهان - حلول الإضاءة", "text", "SEO meta title"),
            ("footer_description",
             "Leading lighting solutions provider delivering innovative and exceptional lighting services across the region.",
             "مزود رائد لحلول الإضاءة يقدم خدمات إضاءة مبتكرة واستثنائية في جميع أنحاء المنطقة.",
             "text", "Footer description"),
            ("footer_copyright", "All rights reserved", "جميع الحقوق محفوظة", "text", "Footer copyright"),
            ("notification_email", "admin@alburhan-regional.com", "admin@alburhan-regional.com", "text", "Email address for contact form notifications"),
        ]
        for key, val_en, val_ar, stype, desc in settings_data:
            existing = db.query(SiteSetting).filter(SiteSetting.key == key).first()
            if existing:
                # keep paths in sync if file has moved
                if existing.setting_type == "image":
                    existing.value_en = val_en
                    existing.value_ar = val_ar
            else:
                db.add(SiteSetting(key=key, value_en=val_en, value_ar=val_ar, setting_type=stype, description=desc))
        print("[+] Site settings seeded")

        # ==================================================================
        # NAVIGATION
        # ==================================================================
        if db.query(NavigationItem).count() == 0:
            nav_items = [
                ("Home", "الرئيسية", "/", "home", 1),
                ("About Us", "من نحن", "/about", "info", 2),
                ("Our Products", "منتجاتنا", "/#products", "inventory", 3),
                ("Our Projects", "مشاريعنا", "/#projects", "work", 4),
                ("Services", "الخدمات", "/#services", "build", 5),
                ("Contact", "اتصل بنا", "/contact", "phone", 6),
            ]
            for label_en, label_ar, href, icon, order in nav_items:
                db.add(NavigationItem(
                    label_en=label_en, label_ar=label_ar,
                    href=href, icon=icon, sort_order=order,
                ))
            print("[+] Navigation items seeded")

        # ==================================================================
        # CAROUSEL SLIDES (hero backgrounds)
        # ==================================================================
        if db.query(CarouselSlide).count() == 0:
            slides = [
                ("Al-Burhan Group", "مجموعة البرهان ",
                 "Light Up Your Life", "إجعل حياتك أكثر إشراقًا ",
                 "Transforming spaces with innovative lighting solutions that blend elegance, functionality, and cutting-edge technology to create breathtaking environments.",
                 "نحوّل المساحات إلى تحف مضيئة عبر حلول إضاءة مبتكرة تمزج بين الأناقة  وأحدث التقنيات، لنصنع بيئات تنبض بالجمال والإبداع.",
                 up("Projects/alburhan1.jpg")),
                ("Innovation", "الابتكار",
                 "Leading Lighting Solutions", "حلول الإضاءة الرائدة",
                 "Pioneering the future of illumination with state-of-the-art LED technology, smart lighting systems, and energy-efficient designs that redefine modern living.",
                 "نرسم مستقبل الإضاءة بتقنيات LED الحديثة، وأنظمة الإضاءة الذكية، والتصاميم الموفّرة للطاقة، لنقدّم تجربة عيش عصرية تجمع بين الأناقة والكفاءة.",
                 up("Projects/alburhan2.jpg")),
                ("Excellence", "التميز",
                 "Premium Quality Products", "منتجات عالية الجودة",
                 "Crafted with precision and passion, our premium lighting collections combine exceptional craftsmanship with luxurious materials to elevate any space.",
                 "صُنعت مجموعات الإضاءة الفاخرة لدينا بدقة وشغف، وتجمع بين الحرفية الاستثنائية والمواد الفاخرة لتُضفي لمسةً مميزة على أي مساحة.",
                 up("Projects/alburhan3.jpg")),
                ("Design", "التصميم",
                 "Elegant Lighting Designs", "تصاميم اضاءة أنيقة ",
                 "Where artistry meets functionality. Our curated designs seamlessly integrate aesthetic beauty with practical innovation, creating timeless pieces that inspire.",
                 "حيث تلتقي البراعة الفنية بالتطبيق العملي. تتكامل تصاميمنا المختارة بعناية مع الجمال الجمالي والابتكار العملي، فنبتكر قطعًا خالدة ملهمة.",
                 up("Projects/alburhan4.jpg")),
                ("Experience", "الخبرة",
                 "20+ Years of Expertise", "اكثر من ٢٠ سنه من الخبرة",
                 "Drawing from over two decades of industry excellence, we deliver unmatched expertise in lighting design, installation, and project implementation across the globe.",
                 "بفضل خبرتنا الممتدة لأكثر من عقدين من التميز في الاضاءة، فإننا نقدم خبرة لا مثيل لها في تصميم الإضاءة وتركيبها وتنفيذ المشاريع في جميع أنحاء العالم.",
                 up("Projects/alburhan5.jpg")),
                ("Quality", "الجودة",
                 "Exceptional Craftsmanship", "حرفية استثنائية",
                 "Every fixture is meticulously engineered and quality-assured, ensuring durability, performance, and lasting beauty that exceeds the highest international standards.",
                 " كل تركيبات الإضاءة لدينا تم تصميمها بعناية فائقة مما يضمن الجودة والمتانة والأداء والجمال الدائم الذي يتجاوز أعلى المعايير الدولية.",
                 up("Projects/alburhan6.jpg")),
                ("Vision", "رؤيتنا",
                 "Illuminating Your Future", "نضيء مستقبلك",
                 "Embracing tomorrow's possibilities today. We envision a world where intelligent lighting transforms how we live, work, and experience our surroundings.",
                 "نحتضن اليوم إمكانيات الغد. نتخيل عالمًا تُغيّر فيه الإضاءة الذكية أسلوب حياتنا وعملنا وتجاربنا مع بيئتنا.",
                 up("Projects/alburhan7.jpg")),
            ]
            for i, (t_en, t_ar, s_en, s_ar, d_en, d_ar, img) in enumerate(slides):
                db.add(CarouselSlide(
                    title_en=t_en, title_ar=t_ar,
                    subtitle_en=s_en, subtitle_ar=s_ar,
                    description_en=d_en, description_ar=d_ar,
                    image_url=img,
                    sort_order=i + 1,
                ))
            print("[+] Carousel slides seeded")

        # ==================================================================
        # COUNTRIES  (firm name, flag, card image, logo)
        # ==================================================================
        if db.query(Country).count() == 0:
            countries_data = [
                ("Kuwait", "الكويت", "kuwait",
                 "Al-Burhan Regional", "البرهان الإقليمية",
                 "Al-Burhan Regional has been a cornerstone of the lighting industry in Kuwait for over two decades. Our extensive network of branches across the country ensures accessibility and exceptional service to clients throughout the region, from residential to commercial projects.",
                 "كان البرهان الإقليمي حجر الزاوية في صناعة الإضاءة في الكويت لأكثر من عقدين. تضمن شبكة فروعنا الواسعة في جميع أنحاء البلاد إمكانية الوصول والخدمة الاستثنائية للعملاء في جميع أنحاء المنطقة، من المشاريع السكنية إلى التجارية.",
                 "https://flagcdn.com/w320/kw.png",
                 up("Countries/alburhan-kuwait.jpg"),
                 up("logo/al burhan kuwait.png"),
                 1),
                ("United Arab Emirates", "الإمارات العربية المتحدة", "uae",
                 "Al-Burhan Hegazi", "البرهان حجازي",
                 "In the heart of Dubai, Al-Burhan Hegazi serves as our gateway to the dynamic Middle Eastern market. We bring innovative lighting solutions to one of the world's most ambitious architectural landscapes, contributing to iconic projects that define modern luxury and sophistication.",
                 "في قلب دبي، يخدم البرهان حجازي كبوابة لنا إلى السوق الشرقي الأوسطي الديناميكي. نجلب حلول إضاءة مبتكرة إلى أحد أكثر المشاريع المعمارية طموحًا في العالم، نساهم في مشاريع أيقونية تحدد الفخامة والأناقة الحديثة.",
                 "https://flagcdn.com/w320/ae.png",
                 up("Countries/alburhan-dubai.jpg"),
                 up("logo/AL BURHAN UAE.png"),
                 2),
                ("China", "الصين", "china",
                 "Al-Bohan", "AL-Bohan",
                 "Al-Burhan's presence in China represents our commitment to manufacturing excellence and innovation. Through our strategic partnerships and state-of-the-art facilities, we deliver world-class lighting solutions that combine quality craftsmanship with cutting-edge technology, serving markets across the globe.",
                 "يمثل وجود البرهان في الصين التزامنا بالتميز في التصنيع والابتكار. من خلال شراكاتنا الاستراتيجية ومرافقنا الحديثة، نقدم حلول إضاءة عالمية المستوى تجمع بين الحرفية المتميزة والتكنولوجيا المتطورة، لخدمة الأسواق في جميع أنحاء العالم.",
                 "https://flagcdn.com/w320/cn.png",
                 up("Countries/alburhan-china.jpg"),
                 up("logo/AL BURHAN CHINA.png"),
                 3),
                ("Egypt", "مصر", "egypt",
                 "Al-Burhan", "البرهان",
                 "Al-Burhan Egypt extends our regional network into North Africa, bringing decades of lighting expertise to Egyptian residential, commercial and hospitality projects.",
                 "يوسّع البرهان مصر شبكتنا الإقليمية إلى شمال إفريقيا، ويجلب خبرة عقود في الإضاءة إلى المشاريع السكنية والتجارية والضيافية في مصر.",
                 "https://flagcdn.com/w320/eg.png",
                 up("Countries/alburhan-egypt.jpg"),
                 up("logo/AL BURHAN EGYPT.png"),
                 4),
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
        kuwait = db.query(Country).filter(Country.slug == "kuwait").first()
        uae = db.query(Country).filter(Country.slug == "uae").first()
        china = db.query(Country).filter(Country.slug == "china").first()
        egypt = db.query(Country).filter(Country.slug == "egypt").first()

        # ==================================================================
        # BANNERS  (country-page hero backgrounds)
        # ==================================================================
        if db.query(Banner).count() == 0:
            country_banners = [
                (kuwait, "Kuwait Hero", "خلفية الكويت", up("Company Countries/kuwait city.jpg"), "hero", "top"),
                (uae, "UAE Hero", "خلفية الإمارات", up("Company Countries/dubai city.jpg"), "hero", "top"),
                (china, "China Hero", "خلفية الصين", up("Company Countries/china city.jpg"), "hero", "top"),
                (egypt, "Egypt Hero", "خلفية مصر", up("Company Countries/egypt city.jpg"), "hero", "top"),
            ]
            for i, (country, n_en, n_ar, img, btype, pos) in enumerate(country_banners):
                if not country:
                    continue
                db.add(Banner(
                    country_id=country.id,
                    name_en=n_en, name_ar=n_ar,
                    image_url=img,
                    banner_type=btype, position=pos,
                    sort_order=i + 1,
                ))
            print("[+] Country hero banners seeded")

        # ==================================================================
        # BRANDS  (logos shown in the home page brand carousel)
        # ==================================================================
        if db.query(Brand).count() == 0:
            brand_files = [
                ("Brand 01", "Brands/brand1.png"),
                ("Brand 02", "Brands/brand2.png"),
                ("Brand 03", "Brands/brand3.png"),
                ("Brand 04", "Brands/brand4.jpg"),
                ("Brand 05", "Brands/brand5.png"),
                ("Brand 06", "Brands/brand6.jpg"),
                ("Brand 07", "Brands/brand7.png"),
                ("Brand 08", "Brands/brand8.png"),
                ("Brand 09", "Brands/brand9.png"),
                ("Brand 09 New", "Brands/brand9new.jpeg"),
                ("Brand 10", "Brands/brand10.png"),
                ("Brand 11", "Brands/brand11.png"),
                ("Brand 12", "Brands/brand12.png"),
                ("Brand 13", "Brands/brand13.png"),
                ("Brand 15", "Brands/brand15.png"),
                ("Kosla", "Brands/kosla_page-0001.jpg"),
            ]
            for i, (name, rel) in enumerate(brand_files):
                db.add(Brand(name=name, logo_url=up(rel), sort_order=i + 1))
            print("[+] Brands seeded")

        # ==================================================================
        # PRODUCTS
        # ==================================================================
        if db.query(Product).count() == 0:
            products = [
                ("Smart Lighting", "الإضاءة الذكية", "Our Product/smart lighting.jpg"),
                ("Commercial Lighting", "الإضاءة التجارية", "Our Product/commercial lighting.jpg"),
                ("Residential Lighting", "الإضاءة السكنية", "Our Product/residential lighting.jpg"),
                ("Industrial Lighting", "الإضاءة الصناعية", "Our Product/industrial lighting.jpg"),
            ]
            for i, (n_en, n_ar, rel) in enumerate(products):
                db.add(Product(name_en=n_en, name_ar=n_ar, image_url=up(rel), sort_order=i + 1))
            print("[+] Products seeded")

        # ==================================================================
        # SERVICES
        # ==================================================================
        if db.query(Service).count() == 0:
            services_data = [
                ("Lighting Design", "تصميم الإضاءة", "Our Service/designing.png", "DesignServices", [
                    ("Project assessment and concept development", "تقييم المشروع وتطوير المفهوم"),
                    ("Interior and exterior lighting layouts", "تخطيطات الإضاءة الداخلية والخارجية"),
                    ("Fixture selection tailored to architectural and decorative needs",
                     "اختيار التركيبات المصممة خصيصًا للاحتياجات المعمارية والديكورية"),
                ]),
                ("Lighting Supply", "توريد الإضاءة", "Our Service/supply.png", "Inventory", [
                    ("A wide range of high-quality indoor and outdoor lighting products",
                     "مجموعة واسعة من منتجات الإضاءة الداخلية والخارجية عالية الجودة"),
                    ("Downlights, spotlights, LED strips, linear lighting, decorative fixtures, façade lighting, and more",
                     "الأنوار المدمجة، والأنوار الموجهة، وشرائط LED، والإضاءة الخطية، والتركيبات الزخرفية، وإضاءة الواجهات، والمزيد"),
                    ("Products selected from trusted global brands",
                     "منتجات مختارة من علامات تجارية عالمية موثوقة"),
                ]),
                ("Supply & Install (Turnkey Solutions)", "التوريد والتركيب (حلول متكاملة)",
                 "Our Service/installation.png", "Build", [
                    ("Complete project execution", "تنفيذ المشروع الكامل"),
                    ("Specialized installation teams", "فرق تركيب متخصصة"),
                    ("On-site coordination with contractors and consultants to ensure optimal results",
                     "التنسيق في الموقع مع المقاولين والاستشاريين لضمان النتائج المثلى"),
                ]),
                ("After-Sales Support", "دعم ما بعد البيع",
                 "Our Service/after sales service.png", "Support", [
                    ("Post-installation follow-up", "المتابعة بعد التركيب"),
                    ("Technical support and maintenance", "الدعم الفني والصيانة"),
                    ("Alternative solutions for future upgrades or modifications",
                     "حلول بديلة للترقيات أو التعديلات المستقبلية"),
                ]),
            ]
            for i, (t_en, t_ar, rel_img, icon, items) in enumerate(services_data):
                svc = Service(title_en=t_en, title_ar=t_ar, image_url=up(rel_img), icon=icon, sort_order=i + 1)
                db.add(svc)
                db.flush()
                for j, (it_en, it_ar) in enumerate(items):
                    db.add(ServiceItem(service_id=svc.id, text_en=it_en, text_ar=it_ar, sort_order=j + 1))
            print("[+] Services seeded")

        # ==================================================================
        # SECTORS
        # ==================================================================
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

        # ==================================================================
        # TEAM MEMBERS (owners + photo)
        # ==================================================================
        if db.query(TeamMember).count() == 0:
            db.add(TeamMember(
                name_en="Mr. Murtaza Bohra", name_ar="السيد مرتضى بوهرا",
                designation_en="Founder", designation_ar="المؤسس",
                quote_en="Twenty years ago, all I had was a small dream to bring something different to the world of lighting.\n\nWe started with humble steps, and over time that dream grew. Today, it has become a name we are proud of Al Burhan Group.\n\nEvery achievement we've made is the result of hard work, dedication, and belief that success comes from honesty and persistence.\n\nI'm proud of everyone who has been part of this journey, and of every light we've brought into people's lives.\n\nOur journey is far from over. Every new project is a new beginning, a new dream to shine brighter.",
                quote_ar="قبل عشرين عامًا، كل ما كان لدي كان حلمًا صغيرًا لجلب شيء مختلف إلى عالم الإضاءة.\n\nبدأنا بخطوات متواضعة، ومع مرور الوقت نما ذلك الحلم. اليوم، أصبح اسماً نفخر به مجموعة البرهان للإضاءة.\n\nكل إنجاز حققناه هو نتيجة العمل الجاد والتفاني والاعتقاد بأن النجاح يأتي من الصدق والمثابرة.\n\nأفتخر بكل من كان جزءًا من هذه الرحلة، وبكل ضوء جلبناه إلى حياة الناس.\n\nرحلتنا لم تنته بعد. كل مشروع جديد هو بداية جديدة، حلم جديد للتألق بشكل أكثر إشراقًا.",
                image_url=up("Owners/Owner1.jpeg"),
                sort_order=1,
            ))
            db.add(TeamMember(
                name_en="Mr. Shabbir Hussain", name_ar="السيد شبير رطلاموالا",
                designation_en="Co-founder", designation_ar="الشريك المؤسس",
                quote_en="It all began with a simple idea to create lighting that inspires and beautifies every space.\n\nToday, that dream has become a reality under the name Al Burhan Group, where quality and creativity are at the heart of every project.\n\nThe journey has been full of challenges, but it has taught us that determination, hard work, and a belief in innovation make all the difference.\n\nI am proud of everyone who has been part of this journey, and of every light we have shared to bring warmth and beauty into people's lives.\n\nBecause we still believe in the dream, every new step is an opportunity to shine even brighter and turn ideas into radiant realities.",
                quote_ar="كل شيء بدأ بفكرة بسيطة لإنشاء إضاءة تلهم وتجمّل كل مساحة.\n\nاليوم، أصبح ذلك الحلم حقيقة تحت اسم مجموعة البرهان  حيث الجودة والإبداع في قلب كل مشروع.\n\nكانت الرحلة مليئة بالتحديات، لكنها علمتنا أن التصميم والعمل الجاد والإيمان بالابتكار يحدثان كل الفرق.\n\nأفتخر بكل من كان جزءًا من هذه الرحلة، وبكل ضوء شاركناه لجلب الدفء والجمال إلى حياة الناس.\n\nلأننا لا نزال نؤمن بالحلم، كل خطوة جديدة هي فرصة للتألق بشكل أكثر إشراقًا وتحويل الأفكار إلى حقائق مشعة.",
                image_url=up("Owners/owner_shabbir.jpeg"),
                sort_order=2,
            ))
            print("[+] Team members seeded")

        # ==================================================================
        # CONTACT INFO (per country)
        # ==================================================================
        if db.query(ContactInfo).count() == 0:
            if kuwait:
                db.add(ContactInfo(
                    country_id=kuwait.id,
                    company_name_en="Al-Burhan Regional", company_name_ar="البرهان الإقليمية",
                    address_en="Kuwait, Hawally, Tunis Street, Al Refaei Building, 4th Floor, Office 5&6",
                    address_ar="الكويت، حولي، شارع تونس، مبنى الرفاعي، الطابق الرابع، مكتب 5 و 6",
                    phone1="+965 99935529", phone2="+965 22280853",
                    email="Info@alburhan-regional.com",
                    business_hours_en="Sat-Thu: 9:00 AM - 7:00 PM, Friday: Closed",
                    business_hours_ar="السبت - الخميس: 9:00 صباحاً - 7:00 مساءً، الجمعة: مغلق",
                    is_head_office=True,
                ))
            if uae:
                db.add(ContactInfo(
                    country_id=uae.id,
                    company_name_en="AL BURHAN HEGAZI GENERAL TRADING LLC",
                    company_name_ar="البرهان حجازي للتجارة العامة ذ.م.م",
                    office_en="OFFICE #13", office_ar="المكتب رقم 13",
                    floor_en="M FLOOR, AL OWAIS BUSINESS TOWER", floor_ar="الطابق M، برج العويس للأعمال",
                    area_en="AL SABHKA, DEIRA", area_ar="الصبخة، ديرة",
                    city_en="DUBAI, UNITED ARAB EMIRATES", city_ar="دبي، الإمارات العربية المتحدة",
                    phone1="+971 56 6032 765", phone2="+971 4 5775 302",
                    email="bdm@alburhan-regional.com",
                ))
            if china:
                db.add(ContactInfo(
                    country_id=china.id,
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
            if egypt:
                db.add(ContactInfo(
                    country_id=egypt.id,
                    company_name_en="Al-Burhan", company_name_ar="البرهان",
                    address_en="Address information to be added",
                    address_ar="معلومات العنوان سيتم إضافتها",
                    phone1="Phone information to be added",
                    email="Email information to be added",
                ))
            print("[+] Contact info seeded")

        # ==================================================================
        # BRANCHES (Kuwait)
        # ==================================================================
        if db.query(Branch).count() == 0 and kuwait:
            branches_data = [
                ("Hawally 1st branch", "فرع حولي الأول",
                 "Tunis street in front of al rehab complex",
                 "شارع تونس مقابل مجمع الرحاب", "66895662"),
                ("Hawally second branch", "فرع حولي الثاني",
                 "Tunis street Opposite Hawalli Governorate",
                 "شارع تونس مقابل محافظة حولي", "69979153"),
                ("Shuweikh branch", "فرع الشويخ",
                 "electricity street", "شارع الكهرباء", "60344088"),
                ("Jahraa branch", "فرع الجهراء",
                 "Jahra Industrial Area", "المنطقة الصناعية بالجهراء", "66890566"),
            ]
            for i, (n_en, n_ar, a_en, a_ar, phone) in enumerate(branches_data):
                db.add(Branch(
                    country_id=kuwait.id, name_en=n_en, name_ar=n_ar,
                    address_en=a_en, address_ar=a_ar, phone1=phone,
                    sort_order=i + 1,
                ))
            print("[+] Branches seeded")

        # ==================================================================
        # SOCIAL LINKS
        # ==================================================================
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

        # ==================================================================
        # FOOTER LINKS
        # ==================================================================
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

        # ==================================================================
        # PROJECT CATEGORIES / PROJECTS / IMAGES
        # Every image path points at a real file under /uploads/OurProject/...
        # ==================================================================
        if db.query(ProjectCategory).count() == 0:
            categories = {
                "Gyms": ("صالات رياضية", [
                    ("Oxygen Gym Jahra", [
                        "OurProject/Oxygen Gym Jahra/IMG-20251130-WA0005.jpg",
                        "OurProject/Oxygen Gym Jahra/IMG-20251130-WA0008.jpg",
                        "OurProject/Oxygen Gym Jahra/IMG-20251130-WA0011.jpg",
                        "OurProject/Oxygen Gym Jahra/IMG-20251130-WA0012.jpg",
                    ]),
                    ("Oxygen Gym KSA", [
                        "OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.06 PM.jpeg",
                        "OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.11 PM..jpeg",
                        "OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.11 PM.jpeg",
                        "OurProject/Oxygen Gym KSA/WhatsApp Image 2026-01-02 at 3.38.35 PM..jpeg",
                    ]),
                    ("Oxygen Gym Mahboula", [
                        "OurProject/Oxygen Gym Mahboula/WhatsApp Image 2025-12-09 at 8.32.33 PM.jpeg",
                        "OurProject/Oxygen Gym Mahboula/WhatsApp Image 2025-12-09 at 8.33.30 PM.jpeg",
                        "OurProject/Oxygen Gym Mahboula/WhatsApp Image 2026-01-02 at 3.38.27 PM (1).jpeg",
                    ]),
                    ("Oxygen Gym UAE", [
                        "OurProject/Oxygen Gym U.A.E/WhatsApp Image 2025-12-09 at 8.33.39 PM.jpeg",
                        "OurProject/Oxygen Gym U.A.E/WhatsApp Image 2025-12-09 at 8.33.43 PM.jpeg",
                        "OurProject/Oxygen Gym U.A.E/WhatsApp Image 2025-12-09 at 8.40.01 PM.jpeg",
                    ]),
                    ("Peak Gym Qurain", [
                        "OurProject/Peak Gym Qurain/WhatsApp Image 2025-12-09 at 8.40.13 PM (1).jpeg",
                        "OurProject/Peak Gym Qurain/WhatsApp Image 2025-12-09 at 8.40.13 PM.jpeg",
                        "OurProject/Peak Gym Qurain/WhatsApp Image 2025-12-09 at 8.40.14 PM (1).jpeg",
                    ]),
                    ("Plage Gym", [
                        "OurProject/Plage Gym/WhatsApp Image 2026-01-02 at 3.38.06 PM.jpeg",
                        "OurProject/Plage Gym/WhatsApp Image 2026-01-02 at 3.38.09 PM..jpeg",
                    ]),
                ]),
                "Restaurants": ("مطاعم", [
                    ("Nandos Al Kout Mall", [
                        "OurProject/Nandos Al Kout Mall/Nandos Al Kout Mall/12.jpg",
                        "OurProject/Nandos Al Kout Mall/Nandos Al Kout Mall/14.jpg",
                        "OurProject/Nandos Al Kout Mall/Nandos Al Kout Mall/5.jpg",
                    ]),
                    ("Wing Stop Al Bida", [
                        "OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.32 AM (1).jpeg",
                        "OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.34 AM.jpeg",
                        "OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.37 AM.jpeg",
                        "OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.41 AM.jpeg",
                        "OurProject/Wing Stop Al Bida/Wing Stop Al Bida/WhatsApp Image 2025-08-23 at 11.30.49 AM.jpeg",
                    ]),
                    ("Wing Stop Salmiya", [
                        "OurProject/Wing Stop Salmiya/Wing Stop Salmiya/WhatsApp Image 2025-08-23 at 11.29.56 AM (2).jpeg",
                        "OurProject/Wing Stop Salmiya/Wing Stop Salmiya/WhatsApp Image 2025-08-23 at 11.29.58 AM.jpeg",
                        "OurProject/Wing Stop Salmiya/Wing Stop Salmiya/WhatsApp Image 2025-08-23 at 11.30.03 AM.jpeg",
                    ]),
                    ("Paul Le Cafe", [
                        "OurProject/Paul Le Cafe/Paul Le Cafe/WhatsApp Image 2025-12-09 at 8.30.21 PM.jpeg",
                    ]),
                    ("Wings Stop Liwan", [
                        "OurProject/Wings Stop Liwan/Wings Stop Liwan/WhatsApp Image 2025-12-09 at 8.33.47 PM.jpeg",
                        "OurProject/Wings Stop Liwan/Wings Stop Liwan/WhatsApp Image 2025-12-09 at 8.33.48 PM (1).jpeg",
                        "OurProject/Wings Stop Liwan/Wings Stop Liwan/WhatsApp Image 2025-12-09 at 8.33.48 PM.jpeg",
                        "OurProject/Wings Stop Liwan/Wings Stop Liwan/WhatsApp Image 2025-12-09 at 8.33.49 PM (1).jpeg",
                    ]),
                    ("Wings Stop Assima Mall", [
                        "OurProject/Wings Stop Assima Mall/Wings Stop Assima Mall/WhatsApp Image 2025-12-09 at 8.33.45 PM (1).jpeg",
                        "OurProject/Wings Stop Assima Mall/Wings Stop Assima Mall/WhatsApp Image 2025-12-09 at 8.33.46 PM.jpeg",
                    ]),
                ]),
                "Showrooms": ("صالات عرض", [
                    ("Dar Al Saback", [
                        "OurProject/Dar Al Saback/Dar Al Saback/WhatsApp Image 2025-12-09 at 8.30.23 PM (1).jpeg",
                        "OurProject/Dar Al Saback/Dar Al Saback/WhatsApp Image 2025-12-09 at 8.30.23 PM.jpeg",
                    ]),
                    ("Beverly Hills", [
                        "OurProject/Beverly Hills/Beverly Hills/WhatsApp Image 2025-08-22 at 1.49.44 PM.jpeg",
                        "OurProject/Beverly Hills/Beverly Hills/WhatsApp Image 2025-08-22 at 1.49.45 PM (1).jpeg",
                        "OurProject/Beverly Hills/Beverly Hills/WhatsApp Image 2025-08-22 at 1.49.45 PM.jpeg",
                    ]),
                    ("Audi Showroom", [
                        "OurProject/Audi Showroom/Audi Showroom/WhatsApp Image 2025-08-23 at 19.37.39_bf3d8686.jpg",
                        "OurProject/Audi Showroom/Audi Showroom/WhatsApp Image 2025-08-26 at 13.10.38_774bc71a.jpg",
                    ]),
                    ("Inglot", [
                        "OurProject/Inglot/Inglot/WhatsApp Image 2025-08-22 at 1.40.37 PM.jpeg",
                        "OurProject/Inglot/Inglot/WhatsApp Image 2025-08-22 at 1.40.39 PM.jpeg",
                        "OurProject/Inglot/Inglot/WhatsApp Image 2025-08-22 at 1.40.42 PM.jpeg",
                    ]),
                    ("Dune London", [
                        "OurProject/Dune London/Dune London/WhatsApp Image 2025-08-22 at 1.49.46 PM.jpeg",
                        "OurProject/Dune London/Dune London/WhatsApp Image 2025-08-22 at 1.49.47 PM (2).jpeg",
                        "OurProject/Dune London/Dune London/WhatsApp Image 2025-08-22 at 1.49.47 PM.jpeg",
                    ]),
                ]),
                "Banks": ("بنوك", [
                    ("Warba Bank", [
                        "OurProject/Warba Bank/Warba Bank/WhatsApp Image 2025-12-09 at 8.30.27 PM.jpeg",
                        "OurProject/Warba Bank/Warba Bank/WhatsApp Image 2025-12-09 at 8.30.28 PM (1).jpeg",
                        "OurProject/Warba Bank/Warba Bank/WhatsApp Image 2025-12-09 at 8.30.28 PM (2).jpeg",
                        "OurProject/Warba Bank/Warba Bank/WhatsApp Image 2025-12-09 at 8.30.28 PM.jpeg",
                    ]),
                    ("HSBC", [
                        "OurProject/HSBC/HSBC/WhatsApp Image 2025-12-09 at 8.30.24 PM (2).jpeg",
                        "OurProject/HSBC/HSBC/WhatsApp Image 2025-12-09 at 8.30.25 PM (1).jpeg",
                        "OurProject/HSBC/HSBC/WhatsApp Image 2025-12-09 at 8.30.25 PM.jpeg",
                    ]),
                ]),
                "Offices": ("مكاتب", [
                    ("STC Office Assima Tower", [
                        "OurProject/STC Office Assima Tower/STC Office Assima Tower/WhatsApp Image 2025-09-29 at 14.22.19.jpeg",
                        "OurProject/STC Office Assima Tower/STC Office Assima Tower/WhatsApp Image 2025-09-29 at 14.22.20 (2).jpeg",
                        "OurProject/STC Office Assima Tower/STC Office Assima Tower/WhatsApp Image 2025-09-29 at 14.22.24.jpeg",
                        "OurProject/STC Office Assima Tower/STC Office Assima Tower/WhatsApp Image 2025-09-29 at 14.22.25 (4).jpeg",
                    ]),
                    ("Zain Al Rai", [
                        "OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.16 PM (2).jpeg",
                        "OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.18 PM (1).jpeg",
                        "OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.19 PM (1).jpeg",
                        "OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.21 PM (1).jpeg",
                        "OurProject/Zain Al Rai/Zain Al Rai/WhatsApp Image 2025-08-22 at 2.26.21 PM.jpeg",
                    ]),
                ]),
            }
            for i, (cat_en, (cat_ar, projs)) in enumerate(categories.items()):
                # Use the first image of the first project as the cover
                cover = up(projs[0][1][0]) if projs and projs[0][1] else None
                cat = ProjectCategory(
                    name_en=cat_en, name_ar=cat_ar,
                    cover_image_url=cover,
                    sort_order=i + 1,
                )
                db.add(cat)
                db.flush()
                for j, (proj_name, images) in enumerate(projs):
                    proj = Project(
                        category_id=cat.id,
                        name_en=proj_name, name_ar=proj_name,
                        sort_order=j + 1,
                    )
                    db.add(proj)
                    db.flush()
                    for k, rel in enumerate(images):
                        db.add(ProjectImage(
                            project_id=proj.id,
                            image_url=up(rel),
                            sort_order=k + 1,
                        ))
            print("[+] Project categories, projects and images seeded")

        # ==================================================================
        # PAGE CONTENT  (section-level images & copy)
        # ==================================================================
        if db.query(PageContent).count() == 0:
            page_contents = [
                # Home hero
                ("home", "hero_logo", None, None, None, None, up("logo/AL BURHAN GROUP .png")),
                ("home", "project_feature", None, None, None, None, up("Projects/Project 1.jpg")),
                # About page
                ("about", "hero_image", None, None, None, None, up("Projects/Experiance.jpg")),
                ("about", "team_group", None, None, None, None, up("OurTeam/ourteam.jpg")),
                # Location markers
                ("shared", "location_pin", None, None, None, None, up("location/locationpin.png")),
                ("shared", "showroom_icon", None, None, None, None, up("location/showroom.png")),
            ]
            for i, (pk, sk, t_en, t_ar, c_en, c_ar, img) in enumerate(page_contents):
                db.add(PageContent(
                    page_key=pk, section_key=sk,
                    title_en=t_en, title_ar=t_ar,
                    content_en=c_en, content_ar=c_ar,
                    image_url=img,
                    sort_order=i + 1,
                ))
            print("[+] Page contents seeded")

        # ==================================================================
        # STATIC PAGES
        # ==================================================================
        if db.query(StaticPage).count() == 0:
            pages = [
                ("privacy", "Privacy Policy", "سياسة الخصوصية",
                 "Privacy policy content here.", "محتوى سياسة الخصوصية هنا."),
                ("terms", "Terms of Service", "شروط الخدمة",
                 "Terms of service content here.", "محتوى شروط الخدمة هنا."),
                ("cookies", "Cookie Policy", "سياسة ملفات تعريف الارتباط",
                 "Cookie policy content here.", "محتوى سياسة ملفات تعريف الارتباط هنا."),
                ("gdpr", "GDPR", "GDPR",
                 "GDPR content here.", "محتوى GDPR هنا."),
            ]
            for slug, t_en, t_ar, c_en, c_ar in pages:
                db.add(StaticPage(slug=slug, title_en=t_en, title_ar=t_ar,
                                  content_en=c_en, content_ar=c_ar))
            print("[+] Static pages seeded")

        # ==================================================================
        # IMAGE BACK-FILL  (force every entity's image_url to point at /uploads/...)
        # Idempotent: safe to re-run after every upload reorganisation.
        # ==================================================================

        # SiteSetting image-type rows
        site_imgs = {
            "logo_url": up("logo/AL BURHAN GROUP .png"),
            "favicon_url": up("locationpin.png"),
        }
        for key, url in site_imgs.items():
            row = db.query(SiteSetting).filter(SiteSetting.key == key).first()
            if row:
                row.value_en = url
                row.value_ar = url

        # Countries: country_image_url + logo_url
        country_imgs = {
            "kuwait": (up("Countries/alburhan-kuwait.jpg"), up("logo/al burhan kuwait.png")),
            "uae": (up("Countries/alburhan-dubai.jpg"), up("logo/AL BURHAN UAE.png")),
            "china": (up("Countries/alburhan-china.jpg"), up("logo/AL BURHAN CHINA.png")),
            "egypt": (up("Countries/alburhan-egypt.jpg"), up("logo/AL BURHAN EGYPT.png")),
        }
        for slug, (img, logo) in country_imgs.items():
            c = db.query(Country).filter(Country.slug == slug).first()
            if c:
                c.country_image_url = img
                c.logo_url = logo

        # Brands by name
        brand_map = {
            "Brand 01": up("Brands/brand1.png"),
            "Brand 02": up("Brands/brand2.png"),
            "Brand 03": up("Brands/brand3.png"),
            "Brand 04": up("Brands/brand4.jpg"),
            "Brand 05": up("Brands/brand5.png"),
            "Brand 06": up("Brands/brand6.jpg"),
            "Brand 07": up("Brands/brand7.png"),
            "Brand 08": up("Brands/brand8.png"),
            "Brand 09": up("Brands/brand9.png"),
            "Brand 09 New": up("Brands/brand9new.jpeg"),
            "Brand 10": up("Brands/brand10.png"),
            "Brand 11": up("Brands/brand11.png"),
            "Brand 12": up("Brands/brand12.png"),
            "Brand 13": up("Brands/brand13.png"),
            "Brand 15": up("Brands/brand15.png"),
            "Kosla": up("Brands/kosla_page-0001.jpg"),
        }
        for name, url in brand_map.items():
            b = db.query(Brand).filter(Brand.name == name).first()
            if b:
                b.logo_url = url

        # Products by english name
        product_map = {
            "Smart Lighting": up("Our Product/smart lighting.jpg"),
            "Commercial Lighting": up("Our Product/commercial lighting.jpg"),
            "Residential Lighting": up("Our Product/residential lighting.jpg"),
            "Industrial Lighting": up("Our Product/industrial lighting.jpg"),
        }
        for name, url in product_map.items():
            p = db.query(Product).filter(Product.name_en == name).first()
            if p:
                p.image_url = url

        # Services
        service_map = {
            "Lighting Design": up("Our Service/designing.png"),
            "Lighting Supply": up("Our Service/supply.png"),
            "Supply & Install (Turnkey Solutions)": up("Our Service/installation.png"),
            "After-Sales Support": up("Our Service/after sales service.png"),
        }
        for title, url in service_map.items():
            s = db.query(Service).filter(Service.title_en == title).first()
            if s:
                s.image_url = url

        # Team members
        team_map = {
            "Mr. Murtaza Bohra": up("Owners/Owner1.jpeg"),
            "Mr. Shabbir Hussain": up("Owners/owner_shabbir.jpeg"),
        }
        for name, url in team_map.items():
            tm = db.query(TeamMember).filter(TeamMember.name_en == name).first()
            if tm:
                tm.image_url = url

        # Carousel slides (match by sort_order)
        carousel_imgs = {
            1: up("Projects/alburhan1.jpg"),
            2: up("Projects/alburhan2.jpg"),
            3: up("Projects/alburhan3.jpg"),
            4: up("Projects/alburhan4.jpg"),
            5: up("Projects/alburhan5.jpg"),
            6: up("Projects/alburhan6.jpg"),
            7: up("Projects/alburhan7.jpg"),
        }
        for order, url in carousel_imgs.items():
            cs = db.query(CarouselSlide).filter(CarouselSlide.sort_order == order).first()
            if cs:
                cs.image_url = url

        # Country hero banners (match country slug + banner_type='hero')
        banner_map = {
            "kuwait": up("Company Countries/kuwait city.jpg"),
            "uae": up("Company Countries/dubai city.jpg"),
            "china": up("Company Countries/china city.jpg"),
            "egypt": up("Company Countries/egypt city.jpg"),
        }
        for slug, url in banner_map.items():
            country = db.query(Country).filter(Country.slug == slug).first()
            if not country:
                continue
            bn = (
                db.query(Banner)
                .filter(Banner.country_id == country.id, Banner.banner_type == "hero")
                .first()
            )
            if bn:
                bn.image_url = url

        # Project category covers — pick first image of the first project per cat
        for cat in db.query(ProjectCategory).all():
            first_proj = (
                db.query(Project)
                .filter(Project.category_id == cat.id)
                .order_by(Project.sort_order)
                .first()
            )
            if not first_proj:
                continue
            first_img = (
                db.query(ProjectImage)
                .filter(ProjectImage.project_id == first_proj.id)
                .order_by(ProjectImage.sort_order)
                .first()
            )
            if first_img and not cat.cover_image_url:
                cat.cover_image_url = first_img.image_url

        # Page contents (back-fill known section images)
        page_imgs = {
            ("home", "hero_logo"): up("logo/AL BURHAN GROUP .png"),
            ("home", "project_feature"): up("Projects/Project 1.jpg"),
            ("about", "hero_image"): up("Projects/Experiance.jpg"),
            ("about", "team_group"): up("OurTeam/ourteam.jpg"),
            ("shared", "location_pin"): up("location/locationpin.png"),
            ("shared", "showroom_icon"): up("location/showroom.png"),
        }
        for (pk, sk), url in page_imgs.items():
            pc = (
                db.query(PageContent)
                .filter(PageContent.page_key == pk, PageContent.section_key == sk)
                .first()
            )
            if pc:
                pc.image_url = url

        print("[+] Image URLs back-filled on existing rows")

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
