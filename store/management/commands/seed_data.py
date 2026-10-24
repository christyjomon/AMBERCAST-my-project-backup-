import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import User, Product, ProductImage, Cart, CartItem, Order, OrderItem, Payment, Inventory, Review

class Command(BaseCommand):
    help = "Seeds database with AmberCast brass art, orders, users, and inventory"

    def handle(self, *args, **options):
        self.stdout.write("Seeding AmberCast database...")

        # 1. Create Users
        admin_user, created = User.objects.get_or_create(
            email="admin@ambercast.com",
            defaults={
                "username": "admin",
                "first_name": "Atelier",
                "last_name": "Guildmaster",
                "phone": "+91 98200 11223",
                "address": "AmberCast Atelier Foundry, Swamimalai, Tamil Nadu, India",
                "role": "Admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write("Created Admin: admin@ambercast.com (Password: admin123)")

        customer_user, created = User.objects.get_or_create(
            email="devraj@heritage.com",
            defaults={
                "username": "devraj",
                "first_name": "Devraj",
                "last_name": "Sengupta",
                "phone": "98201 44921",
                "address": "42/A Heritage Estate, Malabar Hill, Mumbai, MH 400006, India",
                "role": "Customer",
            }
        )
        if created:
            customer_user.set_password("customer123")
            customer_user.save()
            self.stdout.write("Created Customer: devraj@heritage.com (Password: customer123)")

        genevieve_user, created = User.objects.get_or_create(
            email="genevieve.vance@chateau-lyon.eu",
            defaults={
                "username": "genevieve",
                "first_name": "Lady Genevieve",
                "last_name": "Vance",
                "phone": "+33 6 49 11 22 33",
                "address": "Château de Bellevue, 69000 Lyon, France",
                "role": "Customer",
            }
        )
        if created:
            genevieve_user.set_password("customer123")
            genevieve_user.save()

        # 2. Product Catalog
        products_data = [
            {
                "product_name": "Lord Nataraja 18-Inch Lost-Wax Cosmic Dancer",
                "sku": "SKU-BR-9042",
                "category": "Temple Deities",
                "description": "Hand-poured according to ancient Chola dynasty canons. Every arch of fire and tranquil facial contour is individually chased with hand chisels after casting. Features celestial drum (Damaru) and cosmic flame (Agni), balancing atop Apasmara on double lotus pedestal.",
                "price": Decimal("485.00"),
                "original_price": Decimal("560.00"),
                "stock_quantity": 4,
                "weight": "6.2 kg (13.6 lbs)",
                "dimensions": '18.5" x 14.2"',
                "alloy_blend": "82% Cu • 18% Zn Brass",
                "patina_finish": "Smoked Antique Ochre",
                "casting_technique": "Cire-Perdue (Lost-Wax) Sand Casting",
                "provenance": "Swamimalai Chola Bronze Guild",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuDdEEy2H5Axs-hrZww-DAnTpT3uNqSJZ_rft4X1-3i6xJuHNLwvVwbgFOmVKPhq4Gne1c5lDX0vIxkgKBBMnvH6--VWQlJVJsSqHoShpc5-SNGpqZMAEwLEzBO4jxE-lJGggRAN4vRSpu7ipL9PWANzvKbpVrtgVR1gDds0700So1etxIGcv1LNcOJP7qsme5WLARa6BKSy8pd7NuFUWXsfFDxuDePMJt7_LAcYMhY6u49aHFOybxy06A", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuA9OfjNdQAc_sXbaW1ttCO_vqa2AIWFlCM_IIgJBuW_AmxmiUsSNdnxgbxebKqnn2vE_kdpinpg_26JQAJAj7D-ZD7gSOGIqQJmo1ifOrB_qvPXafH_gYMAtkuBCK5-oFUj2eiG7rbQMNV5j7210nElMgccEr5BQIQhgXvUrD-FKIHIDyNY8898eVmhfOfx6XOYm7uIBlKLIYszQL1w6ZX_dMPUhnPH6EGO8MG6XECkToRYIWhlz8t4Yg", False),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuDoCuFvEAj1Kqv7zhCyV7ikjNlrVDvusbJqE0RlcQecdVG26MlQqH_ge5AjvmaHFa3Jk9McuyJYNHgHudhEhaTSjko7DsxobHVrCxlu68KVO5zRvfs9YD4V37IjmpocZYzv82BVK6EOc709uLX04HYIfo0jXq6gCd5ZuMVuR5Lq9JX51znooYO-cRFEkKPGzFwaUraru6yMjsnQi1Sd2rvatepDN6hEs64MJOs2qFgas0lQezkIIZONCw", False),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAH3GOM2A-pe9PQWiu0lM8tB6y2-OdpRcjO8yrf5BINi-S6ZYqGwHeK5fvFWBNKynMQWc_gEqxN-ZiZ_5JgKZlQUhVOhMzEVE0B2fMHmRSeDevstxzXU-8EPJkwjTTfBQvCgBA7NUwYbcd7qHrtuxIYflf1OOloHs6wUzXsCaRvho4xv403ndb6CBgl0lL6VAM3A6uVvWBSW4CwQbhQO2GylDNOraPcu0VhKMyUZX9EZxyRYwXz28evuQ", False),
                ]
            },
            {
                "product_name": "Handcrafted Brass Ganesha Diya",
                "sku": "SKU-BR-GAN09",
                "category": "Temple Deities",
                "description": "Meticulously hand-poured solid antique brass Ganesha Diya sculpture. Features seated Vinayaka on a detailed double lotus throne, holding axe, noose, broken tusk, and sweet modak. Radiates an auspicious and peaceful aura.",
                "price": Decimal("245.00"),
                "original_price": Decimal("285.00"),
                "stock_quantity": 8,
                "weight": "4.2 kg",
                "dimensions": '12" x 9"',
                "alloy_blend": "Virgin Brass Purity 98.4%",
                "patina_finish": "Antique Ochre Burnished",
                "casting_technique": "Sand & Lost-Wax Casting",
                "provenance": "Thanjavur Sacred Icon Guild",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBVCe7WlKvTvYVNlw0DXkK261U1ZPp4ZfrJfgu-h8eQc9hFjcV25BUtLTyb2NQpOcFhJMTh3DTuDDIu8c6TQh7AMsJIBbwkDWSGf--d011ndVKz62KPw6Wvi4UW3Y4Q3xb9ps3GFs30WKTxBiD5Rzw2MYztNgVXHZQu9FyIy7Jgkvv3i0qibonrJUlGvP32Z2Oy6cnRRN7rj0YBkMNaf0EWby4DCpLXdAte6wwbTyaaxqY4c6CNPAwQkQ", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuCv0cptgETVKulo8Fo7ZzlDGrAFLgYX9yNOaiR-FLPKiQCMSK88S6dFTsKFnriyUpplZigORkpwACFYwVIHsZWP-MzC1QMFwTK50Kwul3EiGTaEV4Fhe6W18Wap6qsGPv2aBagxcABEV0HKiE47KMJK8T-nKc8zSGcuMFmk40opzZo1klrbv630CV8BwqcHLYZynrPYyKzGyL1xfly9B6uikZNtbGvVU1Am_IdZLad42Haws4ZkXEz1QQ", False),
                ]
            },
            {
                "product_name": "Antique Brass Peacock Uruli",
                "sku": "SKU-BR-PCK16",
                "category": "Water Urulis & Bowls",
                "description": "Exquisite heavy antique cast brass peacock uruli water bowl with hand-hammered rim and intricately cast dancing peacock handles. Master burnished golden sheen created using traditional tamarind and wood-ash polishing.",
                "price": Decimal("380.00"),
                "original_price": Decimal("440.00"),
                "stock_quantity": 6,
                "weight": "6.8 kg",
                "dimensions": '16" Diameter x 6" Height',
                "alloy_blend": "Solid Bell-Metal Core (80% Cu, 20% Sn/Zn)",
                "patina_finish": "Master Burnished Gold",
                "casting_technique": "Lost-Wax & Hammer Chasing",
                "provenance": "Mannar Bell-Metal Guild",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuCYI95jumpOK6xXP_MZ5lxqYTVFkyu7PejXdmuBTCCYZhEPPj5uTmKsfm6ka5RlZ1LUTh9bbf6N2V9SrSIAzw0qFhm-o_GH2ctCZCYWBUOYgNiMBDbplO0gsuv9aVp3mBeZrk5vMF1NW360o2Gqu9dwM3T6F2PArajN7aCD2lVBe0fEFtMh840fjSNbJ6iQH63Mmx4Lu7Tsdb7GGgMsdVss9WOktZA_kpEQjthAzsDAhRrkY6tJ71iMdw", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAlbKuCCoXHn7zvlR198yYE9Dqdw6GLL1jaMmofGfu6Q2cucMdsL1EDoDHbcRZvl5Owcyekq6jMs8fXzbbnlFpifJ5P6QnKrFmCqu848cNdf0vPHNx2cSaOiXBcWOn5t3wfZw5tJLLIrWhouasmEoxkYlGRjMuumyPAxZB_tt4scLhyNdSxIR2t3s1LhL24wAyZpuy_Ih_Ziukn_3_oUdJQLeSP9zYzFKfIe5uCAQ4q5wLLSJtdsZwAFw", False),
                ]
            },
            {
                "product_name": "Venugopala Krishna in Sand-Cast Brass",
                "sku": "SKU-BR-KRI01",
                "category": "Temple Deities",
                "description": "Hand-poured in Thanjavur. Features Lord Krishna playing flute, standing cross-legged upon a sacred multi-hooded Naga plinth with delicate kadamba garland and peacock feather crest.",
                "price": Decimal("165.00"),
                "original_price": Decimal("210.00"),
                "stock_quantity": 3,
                "weight": "3.2 kg",
                "dimensions": '14" x 6"',
                "alloy_blend": "Virgin Solid Brass (85% Cu, 15% Zn)",
                "patina_finish": "Antique Golden Patina",
                "casting_technique": "Sand-Cast & Chased",
                "provenance": "Thanjavur Foundry #2",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBIFe-Lc7fT3VLEnBZF-6EMQbN282vOvKFKpvvXusFc3B-CTSiJ-64ARCp9AEuJTKCOOClN1xQc36yCaWACM29cceNK3y2xHjV1uQrtw7bxpKfx8rHKUjVdB017cfDPCiMsM34TKedRAn-pAvSOg4ZXPqV6rOCQzfdBrteD3fqnO9Q4FP1xGYzHa1VdYDX20oUg2F3p0zny28QTAxc3uDT7vDV_VoTfBU7QM-kyhzgGEpKWmFyIPVxzCQ", True),
                ]
            },
            {
                "product_name": "Peacock Mayil Kuthu Vilakku Pair",
                "sku": "SKU-BR-PCK12",
                "category": "Ritual Diyas & Deepams",
                "description": "Pair of towering South Indian brass Kuthu Vilakku oil lamps with intricate swan and peacock finials, multi-tier oil reservoirs, and heavy fluted base. Designed for five cotton wicks.",
                "price": Decimal("310.00"),
                "original_price": Decimal("360.00"),
                "stock_quantity": 7,
                "weight": "Pair • 4.5 kg",
                "dimensions": '24" x 8" each',
                "alloy_blend": "Virgin Solid Brass",
                "patina_finish": "Polished Golden Brass",
                "casting_technique": "Lathe Turned & Sand Cast",
                "provenance": "Nachiar Kovil Brass Guild",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBOaW24Spwo-Hf-VRrw0RAC3_WzzPVdn0TGD8k1S3qhJRZUreYFXkF8U5Vpobdv3eipt0rXp3NZumH2xtrGmi8hKxq_fSwFhR6EVQ1xtX-Lnmxb5pdSFZy4kOTTQ2mKXfisiwzovYhj4Ug1_gJRNy8-0y5jIahf7ZC65VR4W04iczhoVyepqcG_TmVshBtHmNkpxWj66-1gU2QbzhgrW8isrWJ2q5MG9N0VpnTii6-0enMubmY3btzNmg", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAILgFrkcf8LT_h87yqqDsprCEfV-i7LQrEI-jkMa9Dlx4BIB68-LN-IpFtqlIAOmigrPDQs5LmvSp6ihvOquyfgSh79sI9SqfB3mo-d9Twgqy__0cIgOY0tAyKN0V7DPO-kA1dLkH2xHZ568vOLq5CCJawRWLiWSK7WuG-sUIT3wrBPXh8OURNQoYplUjAREIq9ts_BQ-AJ6IQiixuzE_UgC330MVmsFh0XRg6AWOnPxY79KO_nO85gg", False),
                ]
            },
            {
                "product_name": "Gaja Lakshmi Temple Diya",
                "sku": "SKU-BR-LAK08",
                "category": "Ritual Diyas & Deepams",
                "description": "Authentic temple architecture lamp featuring twin abhishekam elephants pouring sacred water from pots onto the seated goddess of abundance and auspicious light. Deep oil reservoir and lotus base.",
                "price": Decimal("250.00"),
                "original_price": Decimal("295.00"),
                "stock_quantity": 2,
                "weight": "Height: 16 inches • 5.4 kg",
                "dimensions": '16" x 11"',
                "alloy_blend": "Swamimalai Chola Bronze Lineage",
                "patina_finish": "Hand-Engraved Antique",
                "casting_technique": "Lost-Wax Process",
                "provenance": "Swamimalai Sthapati Collective",
                "is_featured": True,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuDaYovpFMMA-Z1NVpdjWXFn96HMWwtbxhnq5M9kLY4AkQ3up21QL0qdcn8z2A43RQzHI1bub2ndfV_ggbEQsOTLaGlpT-ceL1nfEjXAoYycTUpi9k4PD2W3EKli-tMaXx2o5JPpG0XAB5HuF4noQERgcYcCNiKzY07k9UE8mqsqmMwOYi1sJ_c9K7hPbZwRx_nB7xXVcTxh4pW2WlD_xkGG_HAGO0xrKKdwy6atPWFn9OyPNsXJMXhzaA", True),
                ]
            },
            {
                "product_name": "Goddess Saraswati with Veena",
                "sku": "SKU-BR-SAR07",
                "category": "Temple Deities",
                "description": "Vedic iconography rendering the goddess of knowledge playing the veena. Fine wax modeling captures delicate fingers, veena tuning pegs, pleated attire, and sacred hamsa swan.",
                "price": Decimal("380.00"),
                "original_price": Decimal("430.00"),
                "stock_quantity": 5,
                "weight": "Solid 5.1 kg",
                "dimensions": '15" x 10"',
                "alloy_blend": "85/15 High-Tin Brass",
                "patina_finish": "Smoked Matte Bronze",
                "casting_technique": "Cire-Perdue (Lost Wax)",
                "provenance": "Thanjavur Bronze Artisans",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuDuQn9Pi0K4PrMCA7f8lnhoQW_aVs9g4frMnnUlT33dR99H5msBtk3gkBula8TpVLYBRToPAbBMZGq7sFKKz5lAaGuRTgO68VzruAAwfoo-81D1yhN3DWP8W4QHP6hsVqbUQzKsOK-3hPsMjYOq1AmwNRebg05dE3SZgiZuacewdxHIbpSL0u17V1KwtaY3TFBlZPv3nDget4w_JGNySy9xw6GLE8CUE6UB6kFZrDBuYbJIuPiEBSdIug", True),
                ]
            },
            {
                "product_name": "Classic Hand-Turned Uruli Bowl",
                "sku": "SKU-BR-URL02",
                "category": "Water Urulis & Bowls",
                "description": "Traditional thick-walled Kerala bell metal brass Uruli bowl for auspicious floating jasmine, marigolds, and floating camphor diyas. Heavy rim with hand-turned lathe finish.",
                "price": Decimal("195.00"),
                "original_price": Decimal("230.00"),
                "stock_quantity": 11,
                "weight": "4.0 kg",
                "dimensions": '14" Diameter',
                "alloy_blend": "Kerala Bell Metal (Vellodu)",
                "patina_finish": "Polished Golden Brass",
                "casting_technique": "Bell-Metal Sand Cast",
                "provenance": "Mannar Craftsmen Collective",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBOTVQT81Op9USi-5srgpNofdYqXHJBtKG12q6Gt2kGlJJJ3ky_lC8n7XAwMuKx8MMtBUHRhNqB5cV3SNkOZBDBYwkk4YZJimcgI_AOjsTww_rMfRaoUpfYigqCw8lIN7aLnTAeWTv3XG9fPTlgVWo_Nb_x9HCmpHk6Ab2-pOPVXxDlWpQpRwsaggROaD8dU2aqorvTmCLXM2WAtTaKbwOjaePfmP2ZDCOkEugui3RKbSlc3ZZxppD66g", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBEmWlzCgkfGpRRtnjdz1D-fGZp6xr_W_1bUfTT7SMWVr3zVleqE8t05zXcfO_hn1_0x-6oWYvm2QMyY1unQDieKDgb_IKDj3jF6QURcoq-JpmWHt9mzV0LiM5vGMlILjTNTiW-iKT4vMVbn2A76IS0rPpN23JsNG7oxEz6oG0JQjfIwLORr3TDhaHlOjuH7QJ9unexl9uBrV-CzqMu2oPAySrgdtOQiixbbuojKLRqA7bKto-NHwV3Zg", False),
                ]
            },
            {
                "product_name": "Devotional Recumbent Nandi",
                "sku": "SKU-BR-NAN03",
                "category": "Temple Deities",
                "description": "Recumbent sacred Nandi bull sculpture in heavyweight solid brass with ornate bells collar, hump details, and serene devoted expression. Hand-tooled saddlecloth engravings.",
                "price": Decimal("175.00"),
                "original_price": Decimal("210.00"),
                "stock_quantity": 9,
                "weight": "Solid 2.9 kg",
                "dimensions": '9" x 6"',
                "alloy_blend": "Solid Bell Brass",
                "patina_finish": "Antique Brown Patina",
                "casting_technique": "Solid Mould Pour",
                "provenance": "Kanchipuram Temple Foundry",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBqx5FFAP4oCRlYv5CSVSKZCZ7pyksKkxwy7mGW-bwGbc4GSW6OqVcEXIgVK2oyoCeP4b-nnkMQWGoDQfiPJUgGZpXslTgA6adJLP8A66ogkdm6B9420ChHNcI94Gqc_vyPHB0Z9XShceKSU9LQXUqyeL1TQu8qaNPcVVUlC8CDn2Z_ROF-n-jgBXnGvBgimXkKMVLvAFhIc3kV--2xTWL4rEm_BTD2WgSgEAGvPgNlp59d5dwu1VtzRw", True),
                ]
            },
            {
                "product_name": "Garuda Resonant Temple Bell",
                "sku": "SKU-BR-BEL05",
                "category": "Resonant Ghanta Bells",
                "description": "Heavy ritual temple hanging ghanta bell featuring winged Garuda finial and ornate heavy brass chain links. Sustained acoustic ringing harmonic tuned at 528 Hz.",
                "price": Decimal("220.00"),
                "original_price": Decimal("260.00"),
                "stock_quantity": 14,
                "weight": "Solid 3.5 kg • Acoustic Tuned",
                "dimensions": '24" Total Drop, 8" Bell',
                "alloy_blend": "Acoustic Bronze Cast (80% Cu, 20% Sn)",
                "patina_finish": "Polished Bell Metal",
                "casting_technique": "Resonant Mould Cast",
                "provenance": "Udupi Sacred Bell Works",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBpH1pQrnSDoMnsYmbGDpij46unoymLTFcEqEamKUX2aXKuDwidyVVsgNJ_54TcVPfuTJSd7GkIrJhIFQZ8eHiUZR-M3-D5zyQVrn3GCKEaUJZB2sEemvGPfZwSSACOyLpvk4iYJwqdaGywg6UhAmr3IAfjecUAO9j-6bwYT7NBWHSsLoBt4HQQ6qzD84SnWBrnDxSfFGiSZhrfXZ_7pOg4XJViiKNuvOwj80fmTkoXpu6KiC8G7W1TIw", True),
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuBnEbHuxLq0v29VJMQYHR-6NT6v3tGdGfBqzcpTCb-qZlFBGyQAP1LtY-a_fo2P169CEgPvWG76w4BebTTAVHfE-kAcHUa51opu8kAOYNTB1iwDWxHb89Ll8hsQeJ1d0x3tuqTfl_uaXYiYSCZiuMoj_KKsYqmAnuEKBXM4gAJfrc1m9R9eBT0Titw_N8P6neRBSTQ1EprgmFdZvIB5oaZ8Q4XNBO-XtPW9jcpa98JgjoS_oinV480Xhg", False),
                ]
            },
            {
                "product_name": "Sunstone Amber Brass Sconce",
                "sku": "SKU-BR-9921",
                "category": "Luminaires",
                "description": "Polished solid brass architectural wall sconce with organic natural amber backplate radiating soft golden illumination. Built with naval brass alloy CuZn40.",
                "price": Decimal("1450.00"),
                "original_price": Decimal("1650.00"),
                "stock_quantity": 24,
                "weight": "Naval Brass • 4.8 kg",
                "dimensions": '18" x 7" x 5"',
                "alloy_blend": "Naval Brass CuZn39Pb3",
                "patina_finish": "Polished Golden Brass",
                "casting_technique": "Milled & Hand-Burnished",
                "provenance": "AmberCast Contemporary Atelier",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuCkHLLb-Csqy1SFo2wDAj5dtI8FJcHQDYdv__SmDfuN1D0UI6yCIQX6bWaNZedJmYanpZnZnmZ-0dchk8P9m-GVpJb9YzqzfpRCUgI_hOkMERDymsOC-vj_v4FfdPFrSDw26TyoAYgOMgfon1xzSRyCDZwjpbgSQ0z2f6lqKStlHvkmOs6oUrEj9S-VEqbw6DkUEiqP6UtTGz5oppGZD6YigAzjHREIe7_oH1Jf7Mxid9reyOPgtmXVPQ", True),
                ]
            },
            {
                "product_name": "Chased Laurel Cabinet Pull (Pair)",
                "sku": "SKU-BR-8104",
                "category": "Cabinetry",
                "description": "Hand-chased brass fluted door handle inlaid with raw inclusions Baltic amber. Cast in solid antique bronze and hand-finished with knurled grip detailing.",
                "price": Decimal("290.00"),
                "original_price": Decimal("340.00"),
                "stock_quantity": 3,
                "weight": "Antiqued Bronze • 0.9 kg",
                "dimensions": '8" Length',
                "alloy_blend": "Foundry Bronze & Virgin Amber",
                "patina_finish": "Antique Brown Patina",
                "casting_technique": "Investment Lost-Wax Cast",
                "provenance": "AmberCast Hardware Atelier",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAhPxa5-wmM9SxFdvtkjBmyjqALjIGE9muWKC9hJRZgryiTCbTl40megmJLWmgejOxfwUne6u3-TIVKCJle3vbL8YdWumMmZ385PSkaCUCnMYW7eB7VJEUPrxe2Ucleq9vNfcN03JNxVD5OSZ6mBSugbXyVBqer3_oHUPHCNit3htE0-bLiProM1pV-7DE_pxxOXJOE1kEDpDK4o0Sw_FvokRn2ONhb5T0vXnt5gVcfuMNviNmJAoAysg", True),
                ]
            },
            {
                "product_name": "Apothecary Reliquary Urn",
                "sku": "SKU-BR-7719",
                "category": "Water Urulis & Bowls",
                "description": "Heavy luxury cast brass urn vessel with hand-carved translucent cherry amber lid. Created through five weeks of investment casting and manual burnishing.",
                "price": Decimal("3200.00"),
                "original_price": Decimal("3600.00"),
                "stock_quantity": 2,
                "weight": "Lost Wax Brass • 6.2 kg",
                "dimensions": '14" Height x 9" Base',
                "alloy_blend": "Solid Lost-Wax Core Brass",
                "patina_finish": "Smoked Antique Ochre",
                "casting_technique": "Lost-Wax Process",
                "provenance": "AmberCast Master Reliquary Guild",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAw61NubODYYXb9o2m7HG0FLh-bjKQr3DInkkD2feKDydHDlIhTxV_A5s6hHl9yDoogxm6igEsQOfHatFD_u9XC-sAZb6QbSNVbPh99fiCI7gdHxZ4456ndCJTiMfIa4fzDjvuBTUnsgiOFq02nIpeHOoB-iTrScLNKQ57NLveNRbHSr9EDWXaT2s3kQoGaZSVnLNOYxAWGHJvrfNC0xpZTBLGu3DPreACBBY6TKypj0-x_lHQc1Ay3nA", True),
                ]
            },
            {
                "product_name": "Equinoctial Desk Astrolabe",
                "sku": "SKU-BR-6401",
                "category": "Timepieces",
                "description": "Minimalist heavy brass desk horological mechanism with amber resin Roman numerals floating within a solid milled brass cage. Functional gear movement.",
                "price": Decimal("2180.00"),
                "original_price": Decimal("2450.00"),
                "stock_quantity": 17,
                "weight": "Milled Brass • 3.1 kg",
                "dimensions": '11" x 7" x 7"',
                "alloy_blend": "Instrument Brass CuZn37",
                "patina_finish": "Polished Golden Brass",
                "casting_technique": "High Precision Milled & Cast",
                "provenance": "AmberCast Horology Studio",
                "is_featured": False,
                "images": [
                    ("https://lh3.googleusercontent.com/aida-public/AB6AXuAENy5BE_imhH9QgDjAmj2_ZyQ55uftEU8e51Tt9uBx0pxu7l9YJjcO4MAAMkpmIi7EX4j9fmVfvyRwNpBB66OtjvB9OFpGgYIybOefIHwdYuo8D_RTq1ZgmPPaNkjat2I4YLhe7xvhHoKkIiGSvX2gtoA4kWSBhyDjhbO0xgop632Ls2gjFsXGoQS7l4zvQcQSP1JC_L8cZo7Pm4lazw6uzlkYEcrJa4NvYG33fJ3rmo7TxxAuHjgXrg", True),
                ]
            },
        ]

        created_products = []
        for pdata in products_data:
            images = pdata.pop("images")
            prod, _ = Product.objects.update_or_create(
                sku=pdata["sku"],
                defaults=pdata
            )
            # Sync inventory record
            prod.sync_inventory()

            # Add images
            ProductImage.objects.filter(product=prod).delete()
            for img_url, is_primary in images:
                ProductImage.objects.create(
                    product=prod,
                    image_path=img_url,
                    is_primary=is_primary
                )
            created_products.append(prod)

        self.stdout.write(f"Created {len(created_products)} Products with Inventory records.")

        # 3. Create Cart & Items for Devraj
        cart, _ = Cart.objects.get_or_create(user=customer_user)
        CartItem.objects.filter(cart=cart).delete()

        # Add Ganesha Diya and Peacock Uruli to cart
        p_ganesha = Product.objects.filter(sku="SKU-BR-GAN09").first()
        p_uruli = Product.objects.filter(sku="SKU-BR-PCK16").first()
        if p_ganesha:
            CartItem.objects.create(cart=cart, product=p_ganesha, quantity=1, unit_price=p_ganesha.price)
        if p_uruli:
            CartItem.objects.create(cart=cart, product=p_uruli, quantity=1, unit_price=p_uruli.price)

        self.stdout.write(f"Configured active shopping cart for {customer_user.email}")

        # 4. Create Sample Orders
        orders_data = [
            {
                "order_reference": "#ORD-9801",
                "user": genevieve_user,
                "first_name": "Lady Genevieve",
                "last_name": "Vance",
                "phone": "+33 6 49 11 22 33",
                "shipping_address": "Château de Bellevue, 69000 Lyon, France",
                "total_amount": Decimal("4650.00"),
                "tax_amount": Decimal("139.50"),
                "payment_status": "Paid",
                "order_status": "Processing",
                "payment_method": "Online Payment",
                "product_skus": [("SKU-BR-7719", 1), ("SKU-BR-9921", 1)]
            },
            {
                "order_reference": "#ORD-9798",
                "user": customer_user,
                "first_name": "Marcus",
                "last_name": "Sterling",
                "phone": "+44 20 7946 0912",
                "shipping_address": "Sterling Chambers, 14 Mayfair Square, London W1J 8AJ, UK",
                "total_amount": Decimal("12800.00"),
                "tax_amount": Decimal("384.00"),
                "payment_status": "Paid",
                "order_status": "Shipped",
                "payment_method": "Online Payment",
                "product_skus": [("SKU-BR-9042", 2), ("SKU-BR-6401", 3)]
            },
            {
                "order_reference": "#ORD-9792",
                "user": customer_user,
                "first_name": "Henrik",
                "last_name": "Lindqvist",
                "phone": "+46 8 123 4567",
                "shipping_address": "Strandvägen 47, 114 56 Stockholm, Sweden",
                "total_amount": Decimal("1740.00"),
                "tax_amount": Decimal("52.20"),
                "payment_status": "COD",
                "order_status": "Processing",
                "payment_method": "COD",
                "product_skus": [("SKU-BR-9921", 1), ("SKU-BR-8104", 1)]
            },
            {
                "order_reference": "#ORD-9788",
                "user": customer_user,
                "first_name": "Kensington",
                "last_name": "Archive",
                "phone": "+44 20 7123 8899",
                "shipping_address": "Kensington High Street, London W8 5SA, UK",
                "total_amount": Decimal("6400.00"),
                "tax_amount": Decimal("192.00"),
                "payment_status": "Paid",
                "order_status": "Delivered",
                "payment_method": "Online Payment",
                "product_skus": [("SKU-BR-7719", 2)]
            },
            {
                "order_reference": "#ORD-9785",
                "user": customer_user,
                "first_name": "Sir Arthur",
                "last_name": "Pendelton",
                "phone": "+44 1451 830123",
                "shipping_address": "The Manor House, Stow-on-the-Wold, Gloucestershire GL54 1BN, UK",
                "total_amount": Decimal("890.00"),
                "tax_amount": Decimal("26.70"),
                "payment_status": "Pending",
                "order_status": "Processing",
                "payment_method": "COD",
                "product_skus": [("SKU-BR-PCK12", 1), ("SKU-BR-URL02", 1), ("SKU-BR-8104", 1)]
            },
            {
                "order_reference": "#ORD-9774",
                "user": genevieve_user,
                "first_name": "Elena",
                "last_name": "Rostova",
                "phone": "+371 67 123456",
                "shipping_address": "Alberta Iela 13, Riga LV-1010, Latvia",
                "total_amount": Decimal("5120.00"),
                "tax_amount": Decimal("153.60"),
                "payment_status": "Paid",
                "order_status": "Shipped",
                "payment_method": "Online Payment",
                "product_skus": [("SKU-BR-9042", 1), ("SKU-BR-7719", 1), ("SKU-BR-PCK16", 1)]
            },
        ]

        for odata in orders_data:
            skus = odata.pop("product_skus")
            pmethod = odata.pop("payment_method")
            order, _ = Order.objects.update_or_create(
                order_reference=odata["order_reference"],
                defaults=odata
            )
            OrderItem.objects.filter(order=order).delete()
            for sku, qty in skus:
                prod = Product.objects.filter(sku=sku).first()
                if prod:
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty,
                        unit_price=prod.price,
                        subtotal=prod.price * qty
                    )

            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "payment_method": pmethod,
                    "transaction_id": f"TXN-{random.randint(10000000, 99999999)}" if pmethod != "COD" else None,
                    "amount": order.total_amount,
                    "payment_status": order.payment_status,
                    "payment_date": timezone.now() if order.payment_status == "Paid" else None,
                }
            )

        self.stdout.write("Created Orders and Payments.")

        # 5. Reviews
        p_nataraja = Product.objects.filter(sku="SKU-BR-9042").first()
        if p_nataraja:
            Review.objects.get_or_create(
                user=customer_user,
                product=p_nataraja,
                defaults={
                    "rating": 5,
                    "comment": "The sheer weight of the 18-inch Dancing Nataraja took my breath away. You can feel the solid core. The facial expression has the serenity you only find in century-old temple icons.",
                }
            )

        if p_uruli:
            Review.objects.get_or_create(
                user=customer_user,
                product=p_uruli,
                defaults={
                    "rating": 5,
                    "comment": "Ordered the Royal Elephant-handle Uruli with COD option. It arrived within 3 days in bulletproof wooden crate packaging. Filled with water and floating roses, it is the crown of our living hall.",
                }
            )

        p_bell = Product.objects.filter(sku="SKU-BR-BEL05").first()
        if p_bell:
            Review.objects.get_or_create(
                user=genevieve_user,
                product=p_bell,
                defaults={
                    "rating": 5,
                    "comment": "Shipped seamlessly via DHL with tracking at every step. The acoustic ring of the temple bell is clear and sustains for over 25 seconds. True heirloom purity.",
                }
            )

        self.stdout.write(self.style.SUCCESS("AmberCast database seeded successfully!"))
