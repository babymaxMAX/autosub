"""Internationalization helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Iterable, Mapping

from config.constants import SUPPORTED_LANGUAGES

DEFAULT_LANGUAGE = "en"
FALLBACK_LANGUAGES = ("en", "ru")

TRANSLATIONS_BY_KEY: Dict[str, Dict[str, str]] = {}
TEXT_TRANSLATIONS: Dict[str, Dict[str, str]] = {}


def _normalize_language(language_code: str | None) -> str:
    """Return normalized language code supported by the bot."""
    if not language_code:
        return DEFAULT_LANGUAGE

    normalized = language_code.lower().split("-")[0]
    if normalized in SUPPORTED_LANGUAGES:
        return normalized

    return DEFAULT_LANGUAGE


def resolve_language(user_or_lang: Any | None) -> str:
    """Resolve language code from user model or explicit code."""
    if isinstance(user_or_lang, str):
        return _normalize_language(user_or_lang)

    for attr in ("language_code", "language", "lang"):
        if hasattr(user_or_lang, attr):
            return _normalize_language(getattr(user_or_lang, attr))

    return DEFAULT_LANGUAGE


def register_key(key: str, translations: Dict[str, str], *, alias: str | None = None) -> None:
    """Register translation map for a key and optional english alias."""
    TRANSLATIONS_BY_KEY[key] = translations
    english = alias or translations.get("en")
    if english:
        TEXT_TRANSLATIONS[english] = translations


def register_text(english: str, translations: Dict[str, str]) -> None:
    """Register translation map directly by english text."""
    TEXT_TRANSLATIONS[english] = translations


# Interface buttons
register_key(
    "menu.upload",
    {
        "ru": "🎯 Загрузить через пресет",
        "en": "🎯 Upload with preset",
        "es": "🎯 Subir con preset",
        "fr": "🎯 Importer avec preset",
        "de": "🎯 Mit Preset hochladen",
        "it": "🎯 Carica con preset",
    },
)

register_key(
    "menu.options",
    {
        "ru": "✨ Создать пресет",
        "en": "✨ Create preset",
        "es": "✨ Crear preset",
        "fr": "✨ Créer preset",
        "de": "✨ Preset erstellen",
        "it": "✨ Crea preset",
    },
)

register_key(
    "menu.presets",
    {
        "ru": "📋 Мои пресеты",
        "en": "📋 My presets",
        "es": "📋 Mis presets",
        "fr": "📋 Mes presets",
        "de": "📋 Meine Presets",
        "it": "📋 I miei preset",
    },
)

register_key(
    "menu.plan",
    {
        "ru": "💳 Тариф",
        "en": "💳 Plan",
        "es": "💳 Plan",
        "fr": "💳 Offre",
        "de": "💳 Tarif",
        "it": "💳 Piano",
    },
)

register_key(
    "menu.history",
    {
        "ru": "🧾 История",
        "en": "🧾 History",
        "es": "🧾 Historial",
        "fr": "🧾 Historique",
        "de": "🧾 Verlauf",
        "it": "🧾 Cronologia",
    },
)

register_key(
    "menu.help",
    {
        "ru": "❓ Помощь",
        "en": "❓ Help",
        "es": "❓ Ayuda",
        "fr": "❓ Aide",
        "de": "❓ Hilfe",
        "it": "❓ Aiuto",
    },
)

register_key(
    "menu.language",
    {
        "ru": "🌐 Язык",
        "en": "🌐 Language",
        "es": "🌐 Idioma",
        "fr": "🌐 Langue",
        "de": "🌐 Sprache",
        "it": "🌐 Lingua",
    },
)

# Prompts
register_key(
    "start.choose_action",
    {
        "ru": "",
        "en": "",
        "es": "",
        "fr": "",
        "de": "",
        "it": "",
        "pt": "",
        "pl": "",
        "tr": "",
        "uk": "",
        "ar": "",
        "zh": "",
        "kk": "",
        "tg": "",
        "uz": "",
    },
)

register_key(
    "language.prompt",
    {
        "ru": "Выбор языка интерфейса:",
        "en": "Choose interface language:",
        "es": "Elige el idioma de la interfaz:",
        "fr": "Choisissez la langue de l’interface :",
        "de": "Wähle die Oberflächensprache:",
        "it": "Scegli la lingua dell’interfaccia:",
    },
)

register_key(
    "language.saved",
    {
        "ru": "Язык сохранён",
        "en": "Language saved",
        "es": "Idioma guardado",
        "fr": "Langue enregistrée",
        "de": "Sprache gespeichert",
        "it": "Lingua salvata",
    },
)

register_key(
    "language.ready",
    {
        "ru": "Готово! Можешь отправить видео.",
        "en": "All set! You can send a video now.",
        "es": "¡Listo! Ya puedes enviar un video.",
        "fr": "C’est prêt ! Vous pouvez envoyer une vidéo.",
        "de": "Fertig! Du kannst jetzt ein Video senden.",
        "it": "Fatto! Ora puoi inviare un video.",
    },
)

register_key(
    "language.invalid",
    {
        "ru": "Этот язык пока не поддерживается.",
        "en": "This language is not supported yet.",
        "es": "Este idioma aún no está disponible.",
        "fr": "Cette langue n’est pas encore prise en charge.",
        "de": "Diese Sprache wird noch nicht unterstützt.",
        "it": "Questa lingua non è ancora supportata.",
    },
)

register_key(
    "onboarding.welcome",
    {
        "ru": "Привет! Я AutoSub. Отправь видео, войс или ссылку — верну ролик с субтитрами, переводом, озвучкой и 9:16. Начнём?",
        "en": "Hi! I’m AutoSub. Send a video, voice, or link — I’ll return subtitles, translation, voiceover, and a 9:16 cut. Ready to start?",
        "es": "¡Hola! Soy AutoSub. Envíame un video, voz o enlace y te devolveré subtítulos, traducción, voz en off y formato 9:16. ¿Empezamos?",
        "fr": "Salut ! Je suis AutoSub. Envoie une vidéo, un audio ou un lien — je te renvoie sous-titres, traduction, voix off et format 9:16. On commence ?",
        "de": "Hi! Ich bin AutoSub. Sende ein Video, Voice oder einen Link – ich liefere Untertitel, Übersetzung, Voiceover und 9:16. Los geht’s?",
        "it": "Ciao! Sono AutoSub. Inviami un video, audio o link: ti restituisco sottotitoli, traduzione, doppiaggio e formato 9:16. Partiamo?",
        "pt": "Oi! Eu sou o AutoSub. Envie um vídeo, áudio ou link — devolvo legendas, tradução, voz e formato 9:16. Vamos começar?",
        "pl": "Cześć! Tu AutoSub. Wyślij wideo, głos lub link — oddam napisy, tłumaczenie, lektora i wersję 9:16. Zaczynamy?",
        "tr": "Merhaba! AutoSub ben. Video, ses veya link gönder — sana altyazı, çeviri, seslendirme ve 9:16 formatı veririm. Başlayalım mı?",
        "uk": "Привіт! Я AutoSub. Надішли відео, войс або посилання — поверну ролик із субтитрами, перекладом, озвучкою та форматом 9:16. Почнемо?",
        "ar": "مرحبًا! أنا AutoSub. أرسل فيديو أو صوتًا أو رابطًا، وسأعيده مع ترجمة مكتوبة وترجمة صوتية وتنسيق 9:16. لنبدأ؟",
        "zh": "嗨！我是 AutoSub。发送视频、语音或链接，我会返回字幕、翻译、配音以及 9:16 版本。现在开始？",
        "kk": "Сәлем! Мен AutoSub. Видео, дауыс немесе сілтеме жібер — субтитр, аударма, дыбыстау және 9:16 форматында қайтарамын. Бастаймыз ба?",
        "tg": "Салом! Ман AutoSub. Видео, овоз ё пайванд фиристед — ман бо субтитр, тарҷума, овоз ва формати 9:16 бармегардонам. Оғоз мекунем?",
        "uz": "Salom! Men AutoSub. Video, ovoz yoki havola yuboring — sizga subtitr, tarjima, ovozli versiya va 9:16 formatida qaytaraman. Boshlaymizmi?",
    },
)

register_key(
    "limits.daily",
    {
        "ru": "Вы достигли дневного лимита. Попробуйте завтра или улучшите тариф.",
        "en": "You’ve reached your daily limit. Try again tomorrow or upgrade your plan.",
        "es": "Has alcanzado el límite diario. Vuelve mañana o mejora tu plan.",
        "fr": "Vous avez atteint votre limite quotidienne. Réessayez demain ou améliorez votre offre.",
        "de": "Du hast dein Tageslimit erreicht. Versuche es morgen erneut oder upgrade deinen Tarif.",
        "it": "Hai raggiunto il limite giornaliero. Riprova domani o passa a un piano superiore.",
        "pt": "Você atingiu o limite diário. Tente novamente amanhã ou faça upgrade do plano.",
        "pl": "Osiągnąłeś dzienny limit. Spróbuj jutro lub ulepsz plan.",
        "tr": "Günlük limitine ulaştın. Yarın tekrar dene veya planını yükselt.",
        "uk": "Ти досяг денного ліміту. Спробуй завтра або онови тариф.",
        "ar": "لقد وصلت إلى الحد اليومي. جرّب مرة أخرى غدًا أو قم بترقية خطتك.",
        "zh": "你已达到每日限额。请明天再试或升级套餐。",
        "kk": "Сіз күндік лимитке жеттіңіз. Ертең қайта көріңіз немесе тарифті жаңартыңыз.",
        "tg": "Шумо ба лимити рӯзона расидед. Фардо боз кӯшиш кунед ё нақшаро навсозӣ намоед.",
        "uz": "Kunlik limittingizga yetdingiz. Ertaga qayta urinib ko‘ring yoki tarifni yangilang.",
    },
)

register_key(
    "upsell.free",
    {
        "ru": "Оформи PRO, чтобы получать до 10 минут видео без ограничений и водяного знака.",
        "en": "Upgrade to PRO for up to 10 minutes per video with no limits or watermark.",
        "es": "Pásate a PRO para procesar hasta 10 minutos por video sin límites ni marca de agua.",
        "fr": "Passez à PRO pour traiter jusqu’à 10 minutes par vidéo sans limite ni filigrane.",
        "de": "Upgrade auf PRO für bis zu 10 Minuten pro Video ohne Limits und ohne Wasserzeichen.",
        "it": "Passa a PRO per elaborare fino a 10 minuti per video senza limiti né watermark.",
        "pt": "Faça upgrade para PRO e processe até 10 minutos por vídeo sem limites nem marca d’água.",
        "pl": "Przejdź na PRO, aby przetwarzać do 10 minut wideo bez limitów i znaku wodnego.",
        "tr": "PRO’ya yükselerek video başına 10 dakikaya kadar limitsiz ve filigransız işlem yap.",
        "uk": "Перейди на PRO, щоб обробляти до 10 хвилин без лімітів і водяного знака.",
        "ar": "رقِّ إلى PRO لمعالجة ما يصل إلى 10 دقائق لكل فيديو دون حدود أو علامة مائية.",
        "zh": "升级到 PRO，可处理单个视频长达 10 分钟，无限制且无水印。",
        "kk": "PRO-ға өтіп, әр бейнені 10 минутқа дейін шектеусіз және сутаңбасыз өңде.",
        "tg": "Ба PRO гузаред, то то 10 дақиқа видео бе маҳдудият ва бе тамға коркард кунед.",
        "uz": "PRO ga o‘ting — har bir videoni 10 daqiqagacha cheklovsiz va suv belgisiz qayta ishlang.",
    },
)

register_text(
    "❌ Operation cancelled.",
    {
        "ru": "❌ Операция отменена.",
        "en": "❌ Operation cancelled.",
        "es": "❌ Operación cancelada.",
        "fr": "❌ Opération annulée.",
        "de": "❌ Vorgang abgebrochen.",
        "it": "❌ Operazione annullata.",
        "pt": "❌ Operação cancelada.",
        "pl": "❌ Operacja anulowana.",
        "tr": "❌ İşlem iptal edildi.",
        "uk": "❌ Операцію скасовано.",
        "ar": "❌ تم إلغاء العملية.",
        "zh": "❌ 操作已取消。",
        "kk": "❌ Әрекет тоқтатылды.",
        "tg": "❌ Амал бекор шуд.",
        "uz": "❌ Amal bekor qilindi.",
    },
)

register_text(
    "❌ Unsupported file type",
    {
        "ru": "❌ Неподдерживаемый тип файла",
        "en": "❌ Unsupported file type",
        "es": "❌ Tipo de archivo no admitido",
        "fr": "❌ Type de fichier non pris en charge",
        "de": "❌ Nicht unterstützter Dateityp",
        "it": "❌ Tipo di file non supportato",
        "pt": "❌ Tipo de arquivo não suportado",
        "pl": "❌ Nieobsługiwany typ pliku",
        "tr": "❌ Desteklenmeyen dosya türü",
        "uk": "❌ Непідтримуваний тип файлу",
        "ar": "❌ نوع الملف غير مدعوم",
        "zh": "❌ 不支持的文件类型",
        "kk": "❌ Қолдау көрсетілмейтін файл түрі",
        "tg": "❌ Навъи файл дастгирӣ намешавад",
        "uz": "❌ Qo‘llab-quvvatlanmaydigan fayl turi",
    },
)

register_text(
    "❌ Invalid link. Supported:\n• YouTube\n• TikTok\n• Instagram",
    {
        "ru": "❌ Неверная ссылка. Поддерживаются:\n• YouTube\n• TikTok\n• Instagram",
        "en": "❌ Invalid link. Supported:\n• YouTube\n• TikTok\n• Instagram",
        "es": "❌ Enlace no válido. Admitidos:\n• YouTube\n• TikTok\n• Instagram",
        "fr": "❌ Lien invalide. Pris en charge :\n• YouTube\n• TikTok\n• Instagram",
        "de": "❌ Ungültiger Link. Unterstützt:\n• YouTube\n• TikTok\n• Instagram",
        "it": "❌ Link non valido. Supportati:\n• YouTube\n• TikTok\n• Instagram",
        "pt": "❌ Link inválido. Suportados:\n• YouTube\n• TikTok\n• Instagram",
        "pl": "❌ Nieprawidłowy link. Obsługiwane:\n• YouTube\n• TikTok\n• Instagram",
        "tr": "❌ Geçersiz bağlantı. Desteklenenler:\n• YouTube\n• TikTok\n• Instagram",
        "uk": "❌ Неправильне посилання. Підтримуються:\n• YouTube\n• TikTok\n• Instagram",
        "ar": "❌ رابط غير صالح. المنصات المدعومة:\n• YouTube\n• TikTok\n• Instagram",
        "zh": "❌ 链接无效。支持：\n• YouTube\n• TikTok\n• Instagram",
        "kk": "❌ Жарамсыз сілтеме. Қолдау көрсетіледі:\n• YouTube\n• TikTok\n• Instagram",
        "tg": "❌ Пайванди нодуруст. Дастгирӣ мешаванд:\n• YouTube\n• TikTok\n• Instagram",
        "uz": "❌ Noto‘g‘ri havola. Qo‘llab-quvvatlanadi:\n• YouTube\n• TikTok\n• Instagram",
    },
)

register_text(
    "📤 Send me:\n• Video file\n• Audio file\n• YouTube/TikTok/Instagram link\n\nOr press /cancel to stop",
    {
        "ru": "📤 Отправь:\n• Видео файл\n• Аудио файл\n• Ссылку на YouTube/TikTok/Instagram\n\nИли нажми /cancel для отмены",
        "en": "📤 Send me:\n• Video file\n• Audio file\n• YouTube/TikTok/Instagram link\n\nOr press /cancel to stop",
        "es": "📤 Envíame:\n• Archivo de video\n• Archivo de audio\n• Enlace de YouTube/TikTok/Instagram\n\nO pulsa /cancel para detener",
        "fr": "📤 Envoie-moi :\n• Fichier vidéo\n• Fichier audio\n• Lien YouTube/TikTok/Instagram\n\nOu tape /cancel pour arrêter",
        "de": "📤 Sende mir:\n• Videodatei\n• Audiodatei\n• Link zu YouTube/TikTok/Instagram\n\nOder tippe /cancel zum Abbrechen",
        "it": "📤 Inviami:\n• File video\n• File audio\n• Link YouTube/TikTok/Instagram\n\nOppure digita /cancel per annullare",
        "pt": "📤 Envie:\n• Arquivo de vídeo\n• Arquivo de áudio\n• Link do YouTube/TikTok/Instagram\n\nOu use /cancel para parar",
        "pl": "📤 Wyślij:\n• Plik wideo\n• Plik audio\n• Link YouTube/TikTok/Instagram\n\nAlbo wpisz /cancel, aby przerwać",
        "tr": "📤 Bana gönder:\n• Video dosyası\n• Ses dosyası\n• YouTube/TikTok/Instagram bağlantısı\n\nVeya durdurmak için /cancel yaz",
        "uk": "📤 Надішли:\n• Відеофайл\n• Аудіофайл\n• Посилання YouTube/TikTok/Instagram\n\nАбо введи /cancel, щоб зупинити",
        "ar": "📤 أرسل لي:\n• ملف فيديو\n• ملف صوت\n• رابط YouTube/TikTok/Instagram\n\nأو اكتب ‎/cancel‎ للإيقاف",
        "zh": "📤 发送给我：\n• 视频文件\n• 音频文件\n• YouTube/TikTok/Instagram 链接\n\n或输入 /cancel 结束",
        "kk": "📤 Маған жібер:\n• Видео файл\n• Аудио файл\n• YouTube/TikTok/Instagram сілтемесі\n\nНемесе тоқтату үшін /cancel жаз",
        "tg": "📤 Ба ман фиристед:\n• Файли видео\n• Файли аудио\n• Пайванди YouTube/TikTok/Instagram\n\nЁ /cancel нависед, то қатъ шавад",
        "uz": "📤 Menga yuboring:\n• Video fayl\n• Audio fayl\n• YouTube/TikTok/Instagram havolasi\n\nYoki to‘xtatish uchun /cancel yozing",
    },
)

# Preset upload instructions
register_key(
    "preset.upload.instruction",
    {
        "ru": "🎯 Выберите пресет для обработки видео\n\n📤 Затем отправьте:\n• Видео файл\n• Аудио файл\n• Ссылку на YouTube/TikTok/Instagram\n\nВидео будет обработано с настройками выбранного пресета.",
        "en": "🎯 Choose a preset for video processing\n\n📤 Then send:\n• Video file\n• Audio file\n• YouTube/TikTok/Instagram link\n\nVideo will be processed with the selected preset settings.",
        "es": "🎯 Elige un preset para procesar el video\n\n📤 Luego envía:\n• Archivo de video\n• Archivo de audio\n• Enlace de YouTube/TikTok/Instagram\n\nEl video se procesará con la configuración del preset seleccionado.",
        "fr": "🎯 Choisissez un preset pour traiter la vidéo\n\n📤 Puis envoyez:\n• Fichier vidéo\n• Fichier audio\n• Lien YouTube/TikTok/Instagram\n\nLa vidéo sera traitée avec les paramètres du preset sélectionné.",
        "de": "🎯 Wählen Sie ein Preset für die Videoverarbeitung\n\n📤 Dann senden Sie:\n• Videodatei\n• Audiodatei\n• YouTube/TikTok/Instagram Link\n\nDas Video wird mit den Einstellungen des ausgewählten Presets verarbeitet.",
        "it": "🎯 Scegli un preset per elaborare il video\n\n📤 Poi invia:\n• File video\n• File audio\n• Link YouTube/TikTok/Instagram\n\nIl video sarà elaborato con le impostazioni del preset selezionato.",
    },
)

register_text(
    "📥 Upload: send a video/audio or link.",
    {
        "ru": "📥 Загрузить: отправь видео, аудио или ссылку.",
        "en": "📥 Upload: send a video/audio or link.",
        "es": "📥 Subir: envía un video, audio o enlace.",
        "fr": "📥 Importer : envoie une vidéo, un audio ou un lien.",
        "de": "📥 Hochladen: sende ein Video, Audio oder einen Link.",
        "it": "📥 Carica: invia un video, un audio o un link.",
        "pt": "📥 Enviar: mande um vídeo, áudio ou link.",
        "pl": "📥 Prześlij: wyślij wideo, audio lub link.",
        "tr": "📥 Yükle: video, ses ya da bağlantı gönder.",
        "uk": "📥 Завантажити: надішли відео, аудіо чи посилання.",
        "ar": "📥 رفع: أرسل فيديو أو صوتًا أو رابطًا.",
        "zh": "📥 上传：发送视频、音频或链接。",
        "kk": "📥 Жүктеу: видео, аудио немесе сілтеме жібер.",
        "tg": "📥 Боргузорӣ: видео, аудио ё пайванд фиристед.",
        "uz": "📥 Yuklash: video, audio yoki havola yuboring.",
    },
)

register_key(
    "help.detailed",
    {
        "ru": "📖 Подробная инструкция по использованию AutoSub\n\n🎯 Загрузка через пресет:\n• Выберите готовый пресет с настройками\n• Отправьте видео, аудио или ссылку\n• Получите обработанный результат\n\n✨ Создание пресета:\n• Настройте все параметры обработки\n• Сохраните как персональный пресет\n• Используйте для будущих видео\n\n📋 Управление пресетами:\n• Просматривайте все сохраненные пресеты\n• Редактируйте существующие настройки\n• Удаляйте ненужные пресеты\n\n💳 Тарифы:\n• FREE: до 60 сек, 3 видео/день\n• PRO: до 10 мин, без водяного знака\n• CREATOR: до 30 мин + озвучка\n\n🌐 Язык интерфейса:\nВыберите удобный язык в настройках",
        "en": "📖 Detailed AutoSub usage guide\n\n🎯 Upload with preset:\n• Choose a ready preset with settings\n• Send video, audio or link\n• Get processed result\n\n✨ Create preset:\n• Configure all processing parameters\n• Save as personal preset\n• Use for future videos\n\n📋 Manage presets:\n• View all saved presets\n• Edit existing settings\n• Delete unnecessary presets\n\n💳 Plans:\n• FREE: up to 60 sec, 3 videos/day\n• PRO: up to 10 min, no watermark\n• CREATOR: up to 30 min + voiceover\n\n🌐 Interface language:\nChoose convenient language in settings",
        "es": "📖 Guía detallada de uso de AutoSub\n\n🎯 Subir con preset:\n• Elige un preset listo con configuraciones\n• Envía video, audio o enlace\n• Obtén resultado procesado\n\n✨ Crear preset:\n• Configura todos los parámetros de procesamiento\n• Guarda como preset personal\n• Usa para videos futuros\n\n📋 Gestionar presets:\n• Ver todos los presets guardados\n• Editar configuraciones existentes\n• Eliminar presets innecesarios\n\n💳 Planes:\n• FREE: hasta 60 seg, 3 videos/día\n• PRO: hasta 10 min, sin marca de agua\n• CREATOR: hasta 30 min + voz en off\n\n🌐 Idioma de interfaz:\nElige idioma conveniente en configuraciones",
        "fr": "📖 Guide détaillé d'utilisation d'AutoSub\n\n🎯 Importer avec preset:\n• Choisissez un preset prêt avec paramètres\n• Envoyez vidéo, audio ou lien\n• Obtenez résultat traité\n\n✨ Créer preset:\n• Configurez tous les paramètres de traitement\n• Sauvegardez comme preset personnel\n• Utilisez pour futures vidéos\n\n📋 Gérer presets:\n• Voir tous les presets sauvegardés\n• Modifier paramètres existants\n• Supprimer presets inutiles\n\n💳 Offres:\n• FREE: jusqu'à 60 sec, 3 vidéos/jour\n• PRO: jusqu'à 10 min, sans filigrane\n• CREATOR: jusqu'à 30 min + voix off\n\n🌐 Langue d'interface:\nChoisissez langue pratique dans paramètres",
        "de": "📖 Detaillierte AutoSub Anleitung\n\n🎯 Mit Preset hochladen:\n• Wählen Sie fertiges Preset mit Einstellungen\n• Senden Sie Video, Audio oder Link\n• Erhalten Sie verarbeitetes Ergebnis\n\n✨ Preset erstellen:\n• Konfigurieren Sie alle Verarbeitungsparameter\n• Speichern Sie als persönliches Preset\n• Verwenden Sie für zukünftige Videos\n\n📋 Presets verwalten:\n• Alle gespeicherten Presets anzeigen\n• Bestehende Einstellungen bearbeiten\n• Unnötige Presets löschen\n\n💳 Tarife:\n• FREE: bis 60 Sek, 3 Videos/Tag\n• PRO: bis 10 Min, ohne Wasserzeichen\n• CREATOR: bis 30 Min + Voiceover\n\n🌐 Interface-Sprache:\nWählen Sie bequeme Sprache in Einstellungen",
        "it": "📖 Guida dettagliata all'uso di AutoSub\n\n🎯 Carica con preset:\n• Scegli preset pronto con impostazioni\n• Invia video, audio o link\n• Ottieni risultato elaborato\n\n✨ Crea preset:\n• Configura tutti i parametri di elaborazione\n• Salva come preset personale\n• Usa per video futuri\n\n📋 Gestisci preset:\n• Visualizza tutti i preset salvati\n• Modifica impostazioni esistenti\n• Elimina preset non necessari\n\n💳 Piani:\n• FREE: fino a 60 sec, 3 video/giorno\n• PRO: fino a 10 min, senza watermark\n• CREATOR: fino a 30 min + doppiaggio\n\n🌐 Lingua interfaccia:\nScegli lingua comoda nelle impostazioni",
    },
)

register_text(
    "✅ Subtitles",
    {
        "ru": "✅ Субтитры",
        "en": "✅ Subtitles",
        "es": "✅ Subtítulos",
        "fr": "✅ Sous-titres",
        "de": "✅ Untertitel",
        "it": "✅ Sottotitoli",
        "pt": "✅ Legendas",
        "pl": "✅ Napisy",
        "tr": "✅ Altyazılar",
        "uk": "✅ Субтитри",
        "ar": "✅ ترجمات",
        "zh": "✅ 字幕",
        "kk": "✅ Субтитр",
        "tg": "✅ Субтитрҳо",
        "uz": "✅ Subtitrlari",
    },
)

register_text(
    "↕️ Format 9:16",
    {
        "ru": "↕️ Формат 9:16",
        "en": "↕️ Format 9:16",
        "es": "↕️ Formato 9:16",
        "fr": "↕️ Format 9:16",
        "de": "↕️ Format 9:16",
        "it": "↕️ Formato 9:16",
        "pt": "↕️ Formato 9:16",
        "pl": "↕️ Format 9:16",
        "tr": "↕️ Format 9:16",
        "uk": "↕️ Формат 9:16",
        "ar": "↕️ تنسيق 9:16",
        "zh": "↕️ 9:16 格式",
        "kk": "↕️ Пішім 9:16",
        "tg": "↕️ Формати 9:16",
        "uz": "↕️ Format 9:16",
    },
)

register_text(
    "🌐 Translate",
    {
        "ru": "🌐 Перевод",
        "en": "🌐 Translate",
        "es": "🌐 Traducir",
        "fr": "🌐 Traduire",
        "de": "🌐 Übersetzen",
        "it": "🌐 Traduci",
        "pt": "🌐 Traduzir",
        "pl": "🌐 Tłumaczenie",
        "tr": "🌐 Çeviri",
        "uk": "🌐 Переклад",
        "ar": "🌐 ترجمة",
        "zh": "🌐 翻译",
        "kk": "🌐 Аударма",
        "tg": "🌐 Тарҷума",
        "uz": "🌐 Tarjima",
    },
)

register_text(
    "🗣️ Voiceover",
    {
        "ru": "🗣️ Озвучка",
        "en": "🗣️ Voiceover",
        "es": "🗣️ Doblaje",
        "fr": "🗣️ Voix off",
        "de": "🗣️ Sprecher",
        "it": "🗣️ Doppiaggio",
        "pt": "🗣️ Narração",
        "pl": "🗣️ Lektor",
        "tr": "🗣️ Seslendirme",
        "uk": "🗣️ Озвучка",
        "ar": "🗣️ دبلجة",
        "zh": "🗣️ 配音",
        "kk": "🗣️ Дыбыстау",
        "tg": "🗣️ Озвучонӣ",
        "uz": "🗣️ Ovozlashtirish",
    },
)

register_text(
    "⚙️ More…",
    {
        "ru": "⚙️ Ещё…",
        "en": "⚙️ More…",
        "es": "⚙️ Más…",
        "fr": "⚙️ Plus…",
        "de": "⚙️ Mehr…",
        "it": "⚙️ Altro…",
        "pt": "⚙️ Mais…",
        "pl": "⚙️ Więcej…",
        "tr": "⚙️ Daha fazla…",
        "uk": "⚙️ Ще…",
        "ar": "⚙️ المزيد…",
        "zh": "⚙️ 更多…",
        "kk": "⚙️ Тағы…",
        "tg": "⚙️ Бештар…",
        "uz": "⚙️ Yana…",
    },
)

register_text(
    "✖️ Cancel",
    {
        "ru": "✖️ Отменить",
        "en": "✖️ Cancel",
        "es": "✖️ Cancelar",
        "fr": "✖️ Annuler",
        "de": "✖️ Abbrechen",
        "it": "✖️ Annulla",
        "pt": "✖️ Cancelar",
        "pl": "✖️ Anuluj",
        "tr": "✖️ İptal",
        "uk": "✖️ Скасувати",
        "ar": "✖️ إلغاء",
        "zh": "✖️ 取消",
        "kk": "✖️ Бас тарту",
        "tg": "✖️ Бекор",
        "uz": "✖️ Bekor qilish",
    },
)

register_text(
    "❌ Cancel",
    {
        "ru": "❌ Отменить",
        "en": "❌ Cancel",
        "es": "❌ Cancelar",
        "fr": "❌ Annuler",
        "de": "❌ Abbrechen",
        "it": "❌ Annulla",
        "pt": "❌ Cancelar",
        "pl": "❌ Anuluj",
        "tr": "❌ İptal",
        "uk": "❌ Скасувати",
        "ar": "❌ إلغاء",
        "zh": "❌ 取消",
        "kk": "❌ Бас тарту",
        "tg": "❌ Бекор",
        "uz": "❌ Bekor qilish",
    },
)

register_text(
    "▶️ Start",
    {
        "ru": "▶️ Запустить",
        "en": "▶️ Start",
        "es": "▶️ Iniciar",
        "fr": "▶️ Démarrer",
        "de": "▶️ Starten",
        "it": "▶️ Avvia",
        "pt": "▶️ Iniciar",
        "pl": "▶️ Start",
        "tr": "▶️ Başlat",
        "uk": "▶️ Запустити",
        "ar": "▶️ ابدأ",
        "zh": "▶️ 开始",
        "kk": "▶️ Қосу",
        "tg": "▶️ Оғоз кардан",
        "uz": "▶️ Boshlash",
    },
)

register_text(
    "🔓 Activate PRO",
    {
        "ru": "🔓 Активировать PRO",
        "en": "🔓 Activate PRO",
        "es": "🔓 Activar PRO",
        "fr": "🔓 Activer PRO",
        "de": "🔓 PRO aktivieren",
        "it": "🔓 Attiva PRO",
        "pt": "🔓 Ativar PRO",
        "pl": "🔓 Aktywuj PRO",
        "tr": "🔓 PRO’yu etkinleştir",
        "uk": "🔓 Активувати PRO",
        "ar": "🔓 تفعيل PRO",
        "zh": "🔓 激活 PRO",
        "kk": "🔓 PRO қосу",
        "tg": "🔓 PRO-ро фаъол кунед",
        "uz": "🔓 PRO ni faollashtirish",
    },
)

register_text(
    "🔥 Get CREATOR",
    {
        "ru": "🔥 Взять CREATOR",
        "en": "🔥 Get CREATOR",
        "es": "🔥 Obtener CREATOR",
        "fr": "🔥 Obtenir CREATOR",
        "de": "🔥 CREATOR holen",
        "it": "🔥 Prendi CREATOR",
        "pt": "🔥 Assinar CREATOR",
        "pl": "🔥 Kup CREATOR",
        "tr": "🔥 CREATOR’a geç",
        "uk": "🔥 Отримати CREATOR",
        "ar": "🔥 احصل على CREATOR",
        "zh": "🔥 获取 CREATOR",
        "kk": "🔥 CREATOR алу",
        "tg": "🔥 CREATOR гиред",
        "uz": "🔥 CREATOR tarifini oling",
    },
)

register_text(
    "📅 My Subscription",
    {
        "ru": "📅 Моя подписка",
        "en": "📅 My Subscription",
        "es": "📅 Mi suscripción",
        "fr": "📅 Mon abonnement",
        "de": "📅 Mein Abo",
        "it": "📅 Il mio abbonamento",
        "pt": "📅 Minha assinatura",
        "pl": "📅 Moja subskrypcja",
        "tr": "📅 Aboneliğim",
        "uk": "📅 Моя підписка",
        "ar": "📅 اشتراكي",
        "zh": "📅 我的订阅",
        "kk": "📅 Менің жазылымым",
        "tg": "📅 Обунаи ман",
        "uz": "📅 Mening obunam",
    },
)

register_text(
    "❓ Billing FAQ",
    {
        "ru": "❓ Вопросы по оплате",
        "en": "❓ Billing FAQ",
        "es": "❓ Preguntas de pago",
        "fr": "❓ FAQ facturation",
        "de": "❓ Zahlungs-FAQ",
        "it": "❓ Domande su pagamenti",
        "pt": "❓ Dúvidas de cobrança",
        "pl": "❓ FAQ płatności",
        "tr": "❓ Ödeme SSS",
        "uk": "❓ Питання по оплаті",
        "ar": "❓ أسئلة الفوترة",
        "zh": "❓ 付款常见问题",
        "kk": "❓ Төлем бойынша сұрақтар",
        "tg": "❓ Саволҳои пардохт",
        "uz": "❓ To‘lov bo‘yicha savollar",
    },
)

register_text(
    "ℹ️ Learn more",
    {
        "ru": "ℹ️ Подробнее",
        "en": "ℹ️ Learn more",
        "es": "ℹ️ Más info",
        "fr": "ℹ️ En savoir plus",
        "de": "ℹ️ Mehr erfahren",
        "it": "ℹ️ Scopri di più",
        "pt": "ℹ️ Saiba mais",
        "pl": "ℹ️ Dowiedz się więcej",
        "tr": "ℹ️ Daha fazla bilgi",
        "uk": "ℹ️ Докладніше",
        "ar": "ℹ️ المزيد من المعلومات",
        "zh": "ℹ️ 了解更多",
        "kk": "ℹ️ Толығырақ",
        "tg": "ℹ️ Маълумоти бештар",
        "uz": "ℹ️ Batafsil",
    },
)

register_text(
    "Up to 3 min (29₽)",
    {
        "ru": "До 3 мин (29₽)",
        "en": "Up to 3 min (29₽)",
        "es": "Hasta 3 min (29₽)",
        "fr": "Jusqu’à 3 min (29₽)",
        "de": "Bis 3 Min (29₽)",
        "it": "Fino a 3 min (29₽)",
        "pt": "Até 3 min (29₽)",
        "pl": "Do 3 min (29₽)",
        "tr": "3 dakikaya kadar (29₽)",
        "uk": "До 3 хв (29₽)",
        "ar": "حتى 3 دقائق (29₽)",
        "zh": "最长 3 分钟 (29₽)",
        "kk": "3 мин дейін (29₽)",
        "tg": "То 3 дақ (29₽)",
        "uz": "3 daqiqagacha (29₽)",
    },
)

register_text(
    "Up to 10 min (49₽)",
    {
        "ru": "До 10 мин (49₽)",
        "en": "Up to 10 min (49₽)",
        "es": "Hasta 10 min (49₽)",
        "fr": "Jusqu’à 10 min (49₽)",
        "de": "Bis 10 Min (49₽)",
        "it": "Fino a 10 min (49₽)",
        "pt": "Até 10 min (49₽)",
        "pl": "Do 10 min (49₽)",
        "tr": "10 dakikaya kadar (49₽)",
        "uk": "До 10 хв (49₽)",
        "ar": "حتى 10 دقائق (49₽)",
        "zh": "最长 10 分钟 (49₽)",
        "kk": "10 мин дейін (49₽)",
        "tg": "То 10 дақ (49₽)",
        "uz": "10 daqiqagacha (49₽)",
    },
)

register_text(
    "Up to 30 min (59₽)",
    {
        "ru": "До 30 мин (59₽)",
        "en": "Up to 30 min (59₽)",
        "es": "Hasta 30 min (59₽)",
        "fr": "Jusqu’à 30 min (59₽)",
        "de": "Bis 30 Min (59₽)",
        "it": "Fino a 30 min (59₽)",
        "pt": "Até 30 min (59₽)",
        "pl": "Do 30 min (59₽)",
        "tr": "30 dakikaya kadar (59₽)",
        "uk": "До 30 хв (59₽)",
        "ar": "حتى 30 دقيقة (59₽)",
        "zh": "最长 30 分钟 (59₽)",
        "kk": "30 мин дейін (59₽)",
        "tg": "То 30 дақ (59₽)",
        "uz": "30 daqiqagacha (59₽)",
    },
)

register_text(
    "◀️ Back",
    {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
        "es": "◀️ Atrás",
        "fr": "◀️ Retour",
        "de": "◀️ Zurück",
        "it": "◀️ Indietro",
        "pt": "◀️ Voltar",
        "pl": "◀️ Wstecz",
        "tr": "◀️ Geri",
        "uk": "◀️ Назад",
        "ar": "◀️ رجوع",
        "zh": "◀️ 返回",
        "kk": "◀️ Артқа",
        "tg": "◀️ Қафо",
        "uz": "◀️ Orqaga",
    },
)

register_text(
    "⬅️ Back",
    {
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
        "es": "⬅️ Atrás",
        "fr": "⬅️ Retour",
        "de": "⬅️ Zurück",
        "it": "⬅️ Indietro",
        "pt": "⬅️ Voltar",
        "pl": "⬅️ Wstecz",
        "tr": "⬅️ Geri",
        "uk": "⬅️ Назад",
        "ar": "⬅️ رجوع",
        "zh": "⬅️ 返回",
        "kk": "⬅️ Артқа",
        "tg": "⬅️ Қафо",
        "uz": "⬅️ Orqaga",
    },
)

register_text(
    "📡 Live Tasks",
    {
        "ru": "📡 Текущие задачи",
        "en": "📡 Live Tasks",
        "es": "📡 Tareas en curso",
        "fr": "📡 Tâches en direct",
        "de": "📡 Laufende Aufgaben",
        "it": "📡 Attività in corso",
        "pt": "📡 Tarefas ao vivo",
        "pl": "📡 Bieżące zadania",
        "tr": "📡 Canlı işler",
        "uk": "📡 Поточні задачі",
        "ar": "📡 المهام الجارية",
        "zh": "📡 当前任务",
        "kk": "📡 Ағымдағы тапсырмалар",
        "tg": "📡 Вазифаҳои ҷорӣ",
        "uz": "📡 Joriy vazifalar",
    },
)

register_text(
    "🚨 Errors",
    {
        "ru": "🚨 Ошибки",
        "en": "🚨 Errors",
        "es": "🚨 Errores",
        "fr": "🚨 Erreurs",
        "de": "🚨 Fehler",
        "it": "🚨 Errori",
        "pt": "🚨 Erros",
        "pl": "🚨 Błędy",
        "tr": "🚨 Hatalar",
        "uk": "🚨 Помилки",
        "ar": "🚨 أخطاء",
        "zh": "🚨 错误",
        "kk": "🚨 Қателер",
        "tg": "🚨 Хатоҳо",
        "uz": "🚨 Xatolar",
    },
)

register_text(
    "👤 User",
    {
        "ru": "👤 Пользователь",
        "en": "👤 User",
        "es": "👤 Usuario",
        "fr": "👤 Utilisateur",
        "de": "👤 Benutzer",
        "it": "👤 Utente",
        "pt": "👤 Usuário",
        "pl": "👤 Użytkownik",
        "tr": "👤 Kullanıcı",
        "uk": "👤 Користувач",
        "ar": "👤 مستخدم",
        "zh": "👤 用户",
        "kk": "👤 Пайдаланушы",
        "tg": "👤 Корбар",
        "uz": "👤 Foydalanuvchi",
    },
)

register_text(
    "💰 Payments",
    {
        "ru": "💰 Платежи",
        "en": "💰 Payments",
        "es": "💰 Pagos",
        "fr": "💰 Paiements",
        "de": "💰 Zahlungen",
        "it": "💰 Pagamenti",
        "pt": "💰 Pagamentos",
        "pl": "💰 Płatności",
        "tr": "💰 Ödemeler",
        "uk": "💰 Платежі",
        "ar": "💰 المدفوعات",
        "zh": "💰 支付",
        "kk": "💰 Төлемдер",
        "tg": "💰 Пардохтҳо",
        "uz": "💰 To‘lovlar",
    },
)

register_text(
    "🧮 Metrics",
    {
        "ru": "🧮 Метрики",
        "en": "🧮 Metrics",
        "es": "🧮 Métricas",
        "fr": "🧮 Métriques",
        "de": "🧮 Kennzahlen",
        "it": "🧮 Metriche",
        "pt": "🧮 Métricas",
        "pl": "🧮 Metryki",
        "tr": "🧮 Metrikler",
        "uk": "🧮 Метрики",
        "ar": "🧮 المؤشرات",
        "zh": "🧮 指标",
        "kk": "🧮 Метрикалар",
        "tg": "🧮 Метрҳо",
        "uz": "🧮 Ko‘rsatkichlar",
    },
)

register_text(
    "🧰 Tools",
    {
        "ru": "🧰 Инструменты",
        "en": "🧰 Tools",
        "es": "🧰 Herramientas",
        "fr": "🧰 Outils",
        "de": "🧰 Werkzeuge",
        "it": "🧰 Strumenti",
        "pt": "🧰 Ferramentas",
        "pl": "🧰 Narzędzia",
        "tr": "🧰 Araçlar",
        "uk": "🧰 Інструменти",
        "ar": "🧰 الأدوات",
        "zh": "🧰 工具",
        "kk": "🧰 Құралдар",
        "tg": "🧰 Абзорҳо",
        "uz": "🧰 Asboblar",
    },
)

register_text(
    "🔄 Auto-detect language",
    {
        "ru": "🔄 Автодетект языка",
        "en": "🔄 Auto-detect language",
        "es": "🔄 Detectar idioma automáticamente",
        "fr": "🔄 Détection automatique",
        "de": "🔄 Sprache automatisch erkennen",
        "it": "🔄 Rileva lingua automaticamente",
        "pt": "🔄 Detectar idioma automaticamente",
        "pl": "🔄 Automatyczne wykrywanie języka",
        "tr": "🔄 Dili otomatik algıla",
        "uk": "🔄 Автовизначення мови",
        "ar": "🔄 اكتشاف اللغة تلقائيًا",
        "zh": "🔄 自动检测语言",
        "kk": "🔄 Тілді автоматты анықтау",
        "tg": "🔄 Забонро худкор муайян кун",
        "uz": "🔄 Tilni avtomatik aniqlash",
    },
)

register_text(
    "🌐 Choose translation language",
    {
        "ru": "🌐 Выбрать язык перевода",
        "en": "🌐 Choose translation language",
        "es": "🌐 Elige el idioma de traducción",
        "fr": "🌐 Choisir la langue de traduction",
        "de": "🌐 Übersetzungssprache wählen",
        "it": "🌐 Scegli la lingua di traduzione",
        "pt": "🌐 Escolha o idioma de tradução",
        "pl": "🌐 Wybierz język tłumaczenia",
        "tr": "🌐 Çeviri dilini seç",
        "uk": "🌐 Обери мову перекладу",
        "ar": "🌐 اختر لغة الترجمة",
        "zh": "🌐 选择翻译语言",
        "kk": "🌐 Аударма тілін таңдаңыз",
        "tg": "🌐 Забони тарҷумаро интихоб кунед",
        "uz": "🌐 Tarjima tilini tanlang",
    },
)

register_text(
    "🌐 Pick translation language:",
    {
        "ru": "🌐 Выберите язык перевода:",
        "en": "🌐 Pick translation language:",
        "es": "🌐 Elige el idioma de traducción:",
        "fr": "🌐 Choisissez la langue de traduction :",
        "de": "🌐 Wähle die Übersetzungssprache:",
        "it": "🌐 Seleziona la lingua di traduzione:",
        "pt": "🌐 Escolha o idioma de tradução:",
        "pl": "🌐 Wybierz język tłumaczenia:",
        "tr": "🌐 Çeviri dilini seç:",
        "uk": "🌐 Оберіть мову перекладу:",
        "ar": "🌐 اختر لغة الترجمة:",
        "zh": "🌐 选择翻译语言：",
        "kk": "🌐 Аударма тілін таңдаңыз:",
        "tg": "🌐 Забони тарҷумаро интихоб кунед:",
        "uz": "🌐 Tarjima tilini tanlang:",
    },
)

register_text(
    "🗣️ Choose TTS voice",
    {
        "ru": "🗣️ Выбрать голос TTS",
        "en": "🗣️ Choose TTS voice",
        "es": "🗣️ Elegir voz TTS",
        "fr": "🗣️ Choisir une voix TTS",
        "de": "🗣️ TTS-Stimme wählen",
        "it": "🗣️ Scegli voce TTS",
        "pt": "🗣️ Escolher voz TTS",
        "pl": "🗣️ Wybierz głos TTS",
        "tr": "🗣️ TTS sesini seç",
        "uk": "🗣️ Обрати голос TTS",
        "ar": "🗣️ اختر صوت TTS",
        "zh": "🗣️ 选择 TTS 声音",
        "kk": "🗣️ TTS дауысын таңдаңыз",
        "tg": "🗣️ Овози TTS-ро интихоб кунед",
        "uz": "🗣️ TTS ovozini tanlang",
    },
)

register_text(
    "🗣️ Choose voice",
    {
        "ru": "🗣️ Выберите голос",
        "en": "🗣️ Choose voice",
        "es": "🗣️ Elige voz",
        "fr": "🗣️ Choisissez une voix",
        "de": "🗣️ Stimme wählen",
        "it": "🗣️ Scegli voce",
        "pt": "🗣️ Escolher voz",
        "pl": "🗣️ Wybierz głos",
        "tr": "🗣️ Ses seç",
        "uk": "🗣️ Оберіть голос",
        "ar": "🗣️ اختر صوتًا",
        "zh": "🗣️ 选择声音",
        "kk": "🗣️ Дауысты таңдаңыз",
        "tg": "🗣️ Овозро интихоб кунед",
        "uz": "🗣️ Ovoz tanlang",
    },
)

register_text(
    "↕️ 9:16",
    {
        "ru": "↕️ 9:16",
        "en": "↕️ 9:16",
        "es": "↕️ 9:16",
        "fr": "↕️ 9:16",
        "de": "↕️ 9:16",
        "it": "↕️ 9:16",
        "pt": "↕️ 9:16",
        "pl": "↕️ 9:16",
        "tr": "↕️ 9:16",
        "uk": "↕️ 9:16",
        "ar": "↕️ 9:16",
        "zh": "↕️ 9:16",
        "kk": "↕️ 9:16",
        "tg": "↕️ 9:16",
        "uz": "↕️ 9:16",
    },
)

register_text(
    "🎚️ Subtitle Style",
    {
        "ru": "🎚️ Стиль субтитров",
        "en": "🎚️ Subtitle Style",
        "es": "🎚️ Estilo de subtítulos",
        "fr": "🎚️ Style des sous-titres",
        "de": "🎚️ Stil der Untertitel",
        "it": "🎚️ Stile dei sottotitoli",
        "pt": "🎚️ Estilo de legendas",
        "pl": "🎚️ Styl napisów",
        "tr": "🎚️ Altyazı stili",
        "uk": "🎚️ Стиль субтитрів",
        "ar": "🎚️ نمط الترجمة",
        "zh": "🎚️ 字幕样式",
        "kk": "🎚️ Субтитр стилі",
        "tg": "🎚️ Услуби субтитр",
        "uz": "🎚️ Subtitr uslubi",
    },
)

register_text(
    "🎚️ Subtitle style",
    {
        "ru": "🎚️ Стиль субтитров",
        "en": "🎚️ Subtitle style",
        "es": "🎚️ Estilo de subtítulos",
        "fr": "🎚️ Style des sous-titres",
        "de": "🎚️ Stil der Untertitel",
        "it": "🎚️ Stile dei sottotitoli",
        "pt": "🎚️ Estilo de legendas",
        "pl": "🎚️ Styl napisów",
        "tr": "🎚️ Altyazı stili",
        "uk": "🎚️ Стиль субтитрів",
        "ar": "🎚️ نمط الترجمة",
        "zh": "🎚️ 字幕样式",
        "kk": "🎚️ Субтитр стилі",
        "tg": "🎚️ Услуби субтитр",
        "uz": "🎚️ Subtitr uslubi",
    },
)

register_text(
    "🔤 Subtitle Language",
    {
        "ru": "🔤 Язык субтитров",
        "en": "🔤 Subtitle Language",
        "es": "🔤 Idioma de subtítulos",
        "fr": "🔤 Langue des sous-titres",
        "de": "🔤 Untertitelsprache",
        "it": "🔤 Lingua dei sottotitoli",
        "pt": "🔤 Idioma das legendas",
        "pl": "🔤 Język napisów",
        "tr": "🔤 Altyazı dili",
        "uk": "🔤 Мова субтитрів",
        "ar": "🔤 لغة الترجمة",
        "zh": "🔤 字幕语言",
        "kk": "🔤 Субтитр тілі",
        "tg": "🔤 Забони субтитр",
        "uz": "🔤 Subtitr tili",
    },
)

register_text(
    "📍 Subtitle Position",
    {
        "ru": "📍 Позиция субтитров",
        "en": "📍 Subtitle Position",
        "es": "📍 Posición de subtítulos",
        "fr": "📍 Position des sous-titres",
        "de": "📍 Position der Untertitel",
        "it": "📍 Posizione dei sottotitoli",
        "pt": "📍 Posição das legendas",
        "pl": "📍 Pozycja napisów",
        "tr": "📍 Altyazı konumu",
        "uk": "📍 Позиція субтитрів",
        "ar": "📍 موضع الترجمة",
        "zh": "📍 字幕位置",
        "kk": "📍 Субтитр орны",
        "tg": "📍 Ҷойгиршавии субтитр",
        "uz": "📍 Subtitr joylashuvi",
    },
)

register_text(
    "💾 Save Preset",
    {
        "ru": "💾 Сохранить пресет",
        "en": "💾 Save Preset",
        "es": "💾 Guardar preset",
        "fr": "💾 Enregistrer preset",
        "de": "💾 Preset speichern",
        "it": "💾 Salva preset",
        "pt": "💾 Salvar preset",
        "pl": "💾 Zapisz preset",
        "tr": "💾 Preseti kaydet",
        "uk": "💾 Зберегти пресет",
        "ar": "💾 حفظ الإعداد",
        "zh": "💾 保存预设",
        "kk": "💾 Пресетті сақтау",
        "tg": "💾 Пресетро захира кунед",
        "uz": "💾 Presetni saqlash",
    },
)

register_text(
    "💾 Save preset",
    {
        "ru": "💾 Сохранить пресет",
        "en": "💾 Save preset",
        "es": "💾 Guardar preset",
        "fr": "💾 Enregistrer preset",
        "de": "💾 Preset speichern",
        "it": "💾 Salva preset",
        "pt": "💾 Salvar preset",
        "pl": "💾 Zapisz preset",
        "tr": "💾 Preseti kaydet",
        "uk": "💾 Зберегти пресет",
        "ar": "💾 حفظ الإعداد",
        "zh": "💾 保存预设",
        "kk": "💾 Пресетті сақтау",
        "tg": "💾 Пресетро захира кунед",
        "uz": "💾 Presetni saqlash",
    },
)

register_text(
    "Custom…",
    {
        "ru": "Кастом…",
        "en": "Custom…",
        "es": "Personalizado…",
        "fr": "Personnalisé…",
        "de": "Individuell…",
        "it": "Personalizzato…",
        "pt": "Personalizado…",
        "pl": "Własne…",
        "tr": "Özel…",
        "uk": "Кастом…",
        "ar": "مخصص…",
        "zh": "自定义…",
        "kk": "Пайдаланушы…",
        "tg": "Фардӣ…",
        "uz": "Moslashtirilgan…",
    },
)

register_text(
    "Sub/36px/Outline1",
    {
        "ru": "Sub/36px/Outline1",
        "en": "Sub/36px/Outline1",
        "es": "Sub/36px/Outline1",
        "fr": "Sub/36px/Outline1",
        "de": "Sub/36px/Outline1",
        "it": "Sub/36px/Outline1",
        "pt": "Sub/36px/Outline1",
        "pl": "Sub/36px/Outline1",
        "tr": "Sub/36px/Outline1",
        "uk": "Sub/36px/Outline1",
        "ar": "Sub/36px/Outline1",
        "zh": "Sub/36px/Outline1",
        "kk": "Sub/36px/Outline1",
        "tg": "Sub/36px/Outline1",
        "uz": "Sub/36px/Outline1",
    },
)

register_text(
    "Clean/32px/NoOutline",
    {
        "ru": "Clean/32px/NoOutline",
        "en": "Clean/32px/NoOutline",
        "es": "Clean/32px/NoOutline",
        "fr": "Clean/32px/NoOutline",
        "de": "Clean/32px/NoOutline",
        "it": "Clean/32px/NoOutline",
        "pt": "Clean/32px/NoOutline",
        "pl": "Clean/32px/NoOutline",
        "tr": "Clean/32px/NoOutline",
        "uk": "Clean/32px/NoOutline",
        "ar": "Clean/32px/NoOutline",
        "zh": "Clean/32px/NoOutline",
        "kk": "Clean/32px/NoOutline",
        "tg": "Clean/32px/NoOutline",
        "uz": "Clean/32px/NoOutline",
    },
)

register_text(
    "Bold/40px/Outline2",
    {
        "ru": "Bold/40px/Outline2",
        "en": "Bold/40px/Outline2",
        "es": "Bold/40px/Outline2",
        "fr": "Bold/40px/Outline2",
        "de": "Bold/40px/Outline2",
        "it": "Bold/40px/Outline2",
        "pt": "Bold/40px/Outline2",
        "pl": "Bold/40px/Outline2",
        "tr": "Bold/40px/Outline2",
        "uk": "Bold/40px/Outline2",
        "ar": "Bold/40px/Outline2",
        "zh": "Bold/40px/Outline2",
        "kk": "Bold/40px/Outline2",
        "tg": "Bold/40px/Outline2",
        "uz": "Bold/40px/Outline2",
    },
)

register_text(
    "Male",
    {
        "ru": "Мужской",
        "en": "Male",
        "es": "Masculino",
        "fr": "Masculin",
        "de": "Männlich",
        "it": "Maschile",
        "pt": "Masculino",
        "pl": "Męski",
        "tr": "Erkek",
        "uk": "Чоловічий",
        "ar": "ذكر",
        "zh": "男声",
        "kk": "Ер",
        "tg": "Мардона",
        "uz": "Erkak",
    },
)

register_text(
    "Female",
    {
        "ru": "Женский",
        "en": "Female",
        "es": "Femenino",
        "fr": "Féminin",
        "de": "Weiblich",
        "it": "Femminile",
        "pt": "Feminino",
        "pl": "Żeński",
        "tr": "Kadın",
        "uk": "Жіночий",
        "ar": "أنثى",
        "zh": "女声",
        "kk": "Әйел",
        "tg": "Занона",
        "uz": "Ayol",
    },
)

register_text(
    "🧩 My presets",
    {
        "ru": "🧩 Мои пресеты",
        "en": "🧩 My presets",
        "es": "🧩 Mis presets",
        "fr": "🧩 Mes presets",
        "de": "🧩 Meine Presets",
        "it": "🧩 I miei preset",
        "pt": "🧩 Meus presets",
        "pl": "🧩 Moje presety",
        "tr": "🧩 Presetlerim",
        "uk": "🧩 Мої пресети",
        "ar": "🧩 إعداداتي",
        "zh": "🧩 我的预设",
        "kk": "🧩 Менің пресеттерім",
        "tg": "🧩 Пресетҳои ман",
        "uz": "🧩 Mening presetlarim",
    },
)

register_text(
    "\nNo presets yet.",
    {
        "ru": "\nПока пусто.",
        "en": "\nNo presets yet.",
        "es": "\nAún no hay presets.",
        "fr": "\nPas encore de presets.",
        "de": "\nNoch keine Presets.",
        "it": "\nNessun preset ancora.",
        "pt": "\nAinda sem presets.",
        "pl": "\nBrak presetów.",
        "tr": "\nHenüz preset yok.",
        "uk": "\nПоки немає пресетів.",
        "ar": "\nلا توجد إعدادات بعد.",
        "zh": "\n暂无预设。",
        "kk": "\nӘзірге пресеттер жоқ.",
        "tg": "\nҲоло пресет нест.",
        "uz": "\nHozircha presetlar yo‘q.",
    },
)

register_text(
    "Deleted",
    {
        "ru": "Удалено",
        "en": "Deleted",
        "es": "Eliminado",
        "fr": "Supprimé",
        "de": "Gelöscht",
        "it": "Eliminato",
        "pt": "Removido",
        "pl": "Usunięto",
        "tr": "Silindi",
        "uk": "Видалено",
        "ar": "تم الحذف",
        "zh": "已删除",
        "kk": "Жойылды",
        "tg": "Нест карда шуд",
        "uz": "O‘chirildi",
    },
)

register_text(
    "Not found",
    {
        "ru": "Не найдено",
        "en": "Not found",
        "es": "No encontrado",
        "fr": "Introuvable",
        "de": "Nicht gefunden",
        "it": "Non trovato",
        "pt": "Não encontrado",
        "pl": "Nie znaleziono",
        "tr": "Bulunamadı",
        "uk": "Не знайдено",
        "ar": "غير موجود",
        "zh": "未找到",
        "kk": "Табылмады",
        "tg": "Ёфт нашуд",
        "uz": "Topilmadi",
    },
)

register_text(
    "Preset saved",
    {
        "ru": "Пресет сохранён",
        "en": "Preset saved",
        "es": "Preset guardado",
        "fr": "Preset enregistré",
        "de": "Preset gespeichert",
        "it": "Preset salvato",
        "pt": "Preset salvo",
        "pl": "Preset zapisany",
        "tr": "Preset kaydedildi",
        "uk": "Пресет збережено",
        "ar": "تم حفظ الإعداد",
        "zh": "预设已保存",
        "kk": "Пресет сақталды",
        "tg": "Пресет захира шуд",
        "uz": "Preset saqlandi",
    },
)

register_text(
    "Preset applied",
    {
        "ru": "Пресет применён",
        "en": "Preset applied",
        "es": "Preset aplicado",
        "fr": "Preset appliqué",
        "de": "Preset angewendet",
        "it": "Preset applicato",
        "pt": "Preset aplicado",
        "pl": "Preset zastosowany",
        "tr": "Preset uygulandı",
        "uk": "Пресет застосовано",
        "ar": "تم تطبيق الإعداد",
        "zh": "预设已应用",
        "kk": "Пресет қолданылды",
        "tg": "Пресет татбиқ шуд",
        "uz": "Preset qo‘llandi",
    },
)

register_text(
    "Preset applied. Send a video or link to process with these options.",
    {
        "ru": "Пресет применён. Отправьте видео или ссылку, чтобы обработать с этими опциями.",
        "en": "Preset applied. Send a video or link to process with these options.",
        "es": "Preset aplicado. Envía un video o enlace para procesar con estas opciones.",
        "fr": "Preset appliqué. Envoyez une vidéo ou un lien à traiter avec ces options.",
        "de": "Preset angewendet. Sende ein Video oder einen Link, um mit diesen Optionen zu verarbeiten.",
        "it": "Preset applicato. Invia un video o un link da elaborare con queste opzioni.",
        "pt": "Preset aplicado. Envie um vídeo ou link para processar com essas opções.",
        "pl": "Preset zastosowany. Wyślij wideo lub link, aby przetworzyć z tymi opcjami.",
        "tr": "Preset uygulandı. Bu seçeneklerle işlemek için video veya bağlantı gönder.",
        "uk": "Пресет застосовано. Надішли відео чи посилання для обробки з цими опціями.",
        "ar": "تم تطبيق الإعداد. أرسل فيديو أو رابطًا للمعالجة بهذه الخيارات.",
        "zh": "预设已应用。发送视频或链接以使用这些选项处理。",
        "kk": "Пресет қолданылды. Осы параметрлермен өңдеу үшін бейне немесе сілтеме жіберіңіз.",
        "tg": "Пресет татбиқ шуд. Видео ё пайванд фиристед, то бо ин танзимот коркард шавад.",
        "uz": "Preset qo‘llandi. Ushbu parametrlar bilan qayta ishlash uchun video yoki havola yuboring.",
    },
)

register_text(
    "Preset not found",
    {
        "ru": "Пресет не найден",
        "en": "Preset not found",
        "es": "Preset no encontrado",
        "fr": "Preset introuvable",
        "de": "Preset nicht gefunden",
        "it": "Preset non trovato",
        "pt": "Preset não encontrado",
        "pl": "Preset nie znaleziony",
        "tr": "Preset bulunamadı",
        "uk": "Пресет не знайдено",
        "ar": "الإعداد غير موجود",
        "zh": "未找到预设",
        "kk": "Пресет табылмады",
        "tg": "Пресет ёфт нашуд",
        "uz": "Preset topilmadi",
    },
)

register_text(
    "Creation coming soon",
    {
        "ru": "Создание скоро",
        "en": "Creation coming soon",
        "es": "Creación muy pronto",
        "fr": "Création bientôt",
        "de": "Erstellung bald verfügbar",
        "it": "Creazione in arrivo",
        "pt": "Criação em breve",
        "pl": "Tworzenie już wkrótce",
        "tr": "Oluşturma yakında",
        "uk": "Створення скоро",
        "ar": "الإنشاء قريبًا",
        "zh": "创建功能即将上线",
        "kk": "Жасау жақында",
        "tg": "Эҷод ба зудӣ",
        "uz": "Yaratish tez orada",
    },
)

register_text(
    "➕ New",
    {
        "ru": "➕ Новый",
        "en": "➕ New",
        "es": "➕ Nuevo",
        "fr": "➕ Nouveau",
        "de": "➕ Neu",
        "it": "➕ Nuovo",
        "pt": "➕ Novo",
        "pl": "➕ Nowy",
        "tr": "➕ Yeni",
        "uk": "➕ Новий",
        "ar": "➕ جديد",
        "zh": "➕ 新建",
        "kk": "➕ Жаңа",
        "tg": "➕ Нав",
        "uz": "➕ Yangi",
    },
)

register_text(
    "Watermark is fixed in Free plan",
    {
        "ru": "Водяной знак доступен только в Free",
        "en": "Watermark is fixed in Free plan",
        "es": "La marca de agua es fija en el plan Free",
        "fr": "Le filigrane est imposé dans l’offre Free",
        "de": "Wasserzeichen ist im Free-Tarif fest",
        "it": "Il watermark è fisso nel piano Free",
        "pt": "A marca d’água é fixa no plano Free",
        "pl": "Znak wodny jest stały w planie Free",
        "tr": "Free planında filigran sabittir",
        "uk": "Водяний знак закріплений у плані Free",
        "ar": "العلامة المائية ثابتة في باقة Free",
        "zh": "Free 套餐中水印固定",
        "kk": "Watermark Free тарифінде тұрақты",
        "tg": "Тамға дар нақшаи Free собит аст",
        "uz": "Free tarifida suv belgisi o‘zgarmaydi",
    },
)

register_text(
    "Toggle unavailable",
    {
        "ru": "Тумблер недоступен",
        "en": "Toggle unavailable",
        "es": "Interruptor no disponible",
        "fr": "Bascule indisponible",
        "de": "Schalter nicht verfügbar",
        "it": "Interruttore non disponibile",
        "pt": "Alternância indisponível",
        "pl": "Przełącznik niedostępny",
        "tr": "Anahtar kullanılamaz",
        "uk": "Перемикач недоступний",
        "ar": "المفتاح غير متاح",
        "zh": "开关不可用",
        "kk": "Ауыстырғыш қолжетімсіз",
        "tg": "Тугла дастрас нест",
        "uz": "O‘zgartirgich mavjud emas",
    },
)

register_text(
    "Voice: {val}",
    {
        "ru": "Голос: {val}",
        "en": "Voice: {val}",
        "es": "Voz: {val}",
        "fr": "Voix : {val}",
        "de": "Stimme: {val}",
        "it": "Voce: {val}",
        "pt": "Voz: {val}",
        "pl": "Głos: {val}",
        "tr": "Ses: {val}",
        "uk": "Голос: {val}",
        "ar": "الصوت: {val}",
        "zh": "声音：{val}",
        "kk": "Дауыс: {val}",
        "tg": "Овоз: {val}",
        "uz": "Ovoz: {val}",
    },
)

register_text(
    "Format: {mode}",
    {
        "ru": "Формат: {mode}",
        "en": "Format: {mode}",
        "es": "Formato: {mode}",
        "fr": "Format : {mode}",
        "de": "Format: {mode}",
        "it": "Formato: {mode}",
        "pt": "Formato: {mode}",
        "pl": "Format: {mode}",
        "tr": "Format: {mode}",
        "uk": "Формат: {mode}",
        "ar": "التنسيق: {mode}",
        "zh": "格式：{mode}",
        "kk": "Пішім: {mode}",
        "tg": "Формат: {mode}",
        "uz": "Format: {mode}",
    },
)

register_text(
    "On: subtitles",
    {
        "ru": "Вкл: субтитры",
        "en": "On: subtitles",
        "es": "Activado: subtítulos",
        "fr": "Activé : sous-titres",
        "de": "An: Untertitel",
        "it": "Attivo: sottotitoli",
        "pt": "Ativado: legendas",
        "pl": "Włączone: napisy",
        "tr": "Açık: altyazı",
        "uk": "Увімкнено: субтитри",
        "ar": "مفعل: ترجمات",
        "zh": "开启：字幕",
        "kk": "Қосулы: субтитр",
        "tg": "Фаъол: субтитр",
        "uz": "Yoqilgan: subtitrlar",
    },
)

register_text(
    "Off: subtitles",
    {
        "ru": "Выкл: субтитры",
        "en": "Off: subtitles",
        "es": "Desactivado: subtítulos",
        "fr": "Désactivé : sous-titres",
        "de": "Aus: Untertitel",
        "it": "Disattivo: sottotitoli",
        "pt": "Desativado: legendas",
        "pl": "Wyłączone: napisy",
        "tr": "Kapalı: altyazı",
        "uk": "Вимкнено: субтитри",
        "ar": "متوقف: ترجمات",
        "zh": "关闭：字幕",
        "kk": "Өшірулі: субтитр",
        "tg": "Ғайрифаъол: субтитр",
        "uz": "O‘chirilgan: subtitrlar",
    },
)

register_text(
    "On: translate",
    {
        "ru": "Вкл: перевод",
        "en": "On: translate",
        "es": "Activado: traducción",
        "fr": "Activé : traduction",
        "de": "An: Übersetzung",
        "it": "Attivo: traduzione",
        "pt": "Ativado: tradução",
        "pl": "Włączone: tłumaczenie",
        "tr": "Açık: çeviri",
        "uk": "Увімкнено: переклад",
        "ar": "مفعل: ترجمة",
        "zh": "开启：翻译",
        "kk": "Қосулы: аударма",
        "tg": "Фаъол: тарҷума",
        "uz": "Yoqilgan: tarjima",
    },
)

register_text(
    "Off: translate",
    {
        "ru": "Выкл: перевод",
        "en": "Off: translate",
        "es": "Desactivado: traducción",
        "fr": "Désactivé : traduction",
        "de": "Aus: Übersetzung",
        "it": "Disattivo: traduzione",
        "pt": "Desativado: tradução",
        "pl": "Wyłączone: tłumaczenie",
        "tr": "Kapalı: çeviri",
        "uk": "Вимкнено: переклад",
        "ar": "متوقف: ترجمة",
        "zh": "关闭：翻译",
        "kk": "Өшірулі: аударма",
        "tg": "Ғайрифаъол: тарҷума",
        "uz": "O‘chirilgan: tarjima",
    },
)

register_text(
    "On: voiceover",
    {
        "ru": "Вкл: озвучка",
        "en": "On: voiceover",
        "es": "Activado: voz en off",
        "fr": "Activé : voix off",
        "de": "An: Voiceover",
        "it": "Attivo: voiceover",
        "pt": "Ativado: narração",
        "pl": "Włączone: lektor",
        "tr": "Açık: seslendirme",
        "uk": "Увімкнено: озвучка",
        "ar": "مفعل: دبلجة",
        "zh": "开启：配音",
        "kk": "Қосулы: дыбыстау",
        "tg": "Фаъол: озвучонӣ",
        "uz": "Yoqilgan: ovozli",
    },
)

register_text(
    "Off: voiceover",
    {
        "ru": "Выкл: озвучка",
        "en": "Off: voiceover",
        "es": "Desactivado: voz en off",
        "fr": "Désactivé : voix off",
        "de": "Aus: Voiceover",
        "it": "Disattivo: voiceover",
        "pt": "Desativado: narração",
        "pl": "Wyłączone: lektor",
        "tr": "Kapalı: seslendirme",
        "uk": "Вимкнено: озвучка",
        "ar": "متوقف: دبلجة",
        "zh": "关闭：配音",
        "kk": "Өшірулі: дыбыстау",
        "tg": "Ғайрифаъол: озвучонӣ",
        "uz": "O‘chirilgan: ovozli",
    },
)

register_text(
    "Format: 9:16",
    {
        "ru": "Формат: 9:16",
        "en": "Format: 9:16",
        "es": "Formato: 9:16",
        "fr": "Format : 9:16",
        "de": "Format: 9:16",
        "it": "Formato: 9:16",
        "pt": "Formato: 9:16",
        "pl": "Format: 9:16",
        "tr": "Format: 9:16",
        "uk": "Формат: 9:16",
        "ar": "التنسيق: ‎9:16‎",
        "zh": "格式：9:16",
        "kk": "Пішім: 9:16",
        "tg": "Формат: 9:16",
        "uz": "Format: 9:16",
    },
)

register_text(
    "Format: original",
    {
        "ru": "Формат: исходный",
        "en": "Format: original",
        "es": "Formato: original",
        "fr": "Format : original",
        "de": "Format: original",
        "it": "Formato: originale",
        "pt": "Formato: original",
        "pl": "Format: oryginalny",
        "tr": "Format: orijinal",
        "uk": "Формат: оригінал",
        "ar": "التنسيق: أصلي",
        "zh": "格式：原始",
        "kk": "Пішім: бастапқы",
        "tg": "Формат: аслӣ",
        "uz": "Format: asl",
    },
)

register_text(
    "🏷️ Watermark on",
    {
        "ru": "🏷️ Водяной знак вкл",
        "en": "🏷️ Watermark on",
        "es": "🏷️ Marca de agua activada",
        "fr": "🏷️ Filigrane activé",
        "de": "🏷️ Wasserzeichen an",
        "it": "🏷️ Watermark attivo",
        "pt": "🏷️ Marca d’água ligada",
        "pl": "🏷️ Znak wodny włączony",
        "tr": "🏷️ Filigran açık",
        "uk": "🏷️ Водяний знак увімкнено",
        "ar": "🏷️ العلامة المائية مفعّلة",
        "zh": "🏷️ 水印开启",
        "kk": "🏷️ Сутаңба қосулы",
        "tg": "🏷️ Тамға фаъол",
        "uz": "🏷️ Suv belgisi yoqilgan",
    },
)

register_text(
    "🏷️ Watermark on/off",
    {
        "ru": "🏷️ Водяной знак on/off",
        "en": "🏷️ Watermark on/off",
        "es": "🏷️ Marca de agua on/off",
        "fr": "🏷️ Filigrane on/off",
        "de": "🏷️ Wasserzeichen an/aus",
        "it": "🏷️ Watermark on/off",
        "pt": "🏷️ Marca d’água on/off",
        "pl": "🏷️ Znak wodny on/off",
        "tr": "🏷️ Filigran açık/kapalı",
        "uk": "🏷️ Водяний знак on/off",
        "ar": "🏷️ العلامة المائية تشغيل/إيقاف",
        "zh": "🏷️ 水印 开/关",
        "kk": "🏷️ Сутаңба on/off",
        "tg": "🏷️ Тамға on/off",
        "uz": "🏷️ Suv belgisi on/off",
    },
)


register_text(
    "Preset creation will be added later. Use “Save preset” in options for now.",
    {
        "ru": "Создание пресетов будет добавлено позже. Используйте «Сохранить пресет» в опциях.",
        "en": "Preset creation will be added later. Use “Save preset” in options for now.",
        "es": "La creación de presets se añadirá más adelante. Usa “Guardar preset” en las opciones por ahora.",
        "fr": "La création de presets sera ajoutée plus tard. Utilisez pour l’instant « Enregistrer preset » dans les options.",
        "de": "Das Erstellen von Presets folgt später. Nutze vorerst „Preset speichern“ in den Optionen.",
        "it": "La creazione dei preset verrà aggiunta più avanti. Per ora usa “Salva preset” nelle opzioni.",
        "pt": "A criação de presets será adicionada depois. Por enquanto use “Salvar preset” nas opções.",
        "pl": "Tworzenie presetów zostanie dodane później. Na razie użyj „Zapisz preset” w opcjach.",
        "tr": "Preset oluşturma daha sonra eklenecek. Şimdilik seçeneklerde “Preset kaydet” seçeneğini kullanın.",
        "uk": "Створення пресетів додадуть пізніше. Поки що користуйся «Зберегти пресет» в опціях.",
        "ar": "سيتم إضافة إنشاء الإعدادات لاحقًا. استخدم «حفظ الإعداد» في الخيارات الآن.",
        "zh": "预设创建功能稍后添加。暂时请在选项中使用“保存预设”。",
        "kk": "Пресет жасау кейін қосылады. Әзірге опциялардағы «Пресетті сақтау» пайдаланыңыз.",
        "tg": "Эҷоди пресет баъдтар илова мешавад. Ҳоло аз «Захира кардани пресет» дар танзимот истифода баред.",
        "uz": "Preset yaratish keyinroq qo‘shiladi. Hozircha parametrlar bo‘limida “Presetni saqlash”dan foydalaning.",
    },
)

register_text(
    "Editing coming soon",
    {
        "ru": "Редактирование скоро",
        "en": "Editing coming soon",
        "es": "Edición muy pronto",
        "fr": "Édition bientôt",
        "de": "Bearbeitung bald verfügbar",
        "it": "Modifica in arrivo",
        "pt": "Edição em breve",
        "pl": "Edycja już wkrótce",
        "tr": "Düzenleme yakında",
        "uk": "Редагування скоро",
        "ar": "التحرير قريبًا",
        "zh": "编辑功能即将上线",
        "kk": "Өңдеу жақында",
        "tg": "Таҳрир ба зудӣ",
        "uz": "Tahrirlash tez orada",
    },
)

register_text(
    "Preset editing will be added soon.",
    {
        "ru": "Редактирование пресетов будет добавлено позже.",
        "en": "Preset editing will be added soon.",
        "es": "La edición de presets se añadirá pronto.",
        "fr": "L’édition de presets sera ajoutée bientôt.",
        "de": "Das Bearbeiten von Presets folgt bald.",
        "it": "La modifica dei preset sarà aggiunta a breve.",
        "pt": "A edição de presets será adicionada em breve.",
        "pl": "Edycja presetów zostanie wkrótce dodana.",
        "tr": "Preset düzenleme yakında eklenecek.",
        "uk": "Редагування пресетів додадуть незабаром.",
        "ar": "سيتم إضافة تعديل الإعدادات قريبًا.",
        "zh": "预设编辑功能即将上线。",
        "kk": "Пресеттерді өңдеу жақында қосылады.",
        "tg": "Таҳрири пресетҳо ба зудӣ илова мешавад.",
        "uz": "Presetlarni tahrirlash tez orada qo‘shiladi.",
    },
)

register_text(
    "Custom style selected",
    {
        "ru": "Кастомный стиль выбран",
        "en": "Custom style selected",
        "es": "Estilo personalizado seleccionado",
        "fr": "Style personnalisé sélectionné",
        "de": "Benutzerdefinierter Stil ausgewählt",
        "it": "Stile personalizzato selezionato",
        "pt": "Estilo personalizado selecionado",
        "pl": "Wybrano styl własny",
        "tr": "Özel stil seçildi",
        "uk": "Кастомний стиль обрано",
        "ar": "تم اختيار النمط المخصص",
        "zh": "已选择自定义样式",
        "kk": "Пайдаланушылық стиль таңдалды",
        "tg": "Услуби фармоишӣ интихоб шуд",
        "uz": "Moslashtirilgan uslub tanlandi",
    },
)

register_text(
    "Style applied",
    {
        "ru": "Стиль применён",
        "en": "Style applied",
        "es": "Estilo aplicado",
        "fr": "Style appliqué",
        "de": "Stil angewendet",
        "it": "Stile applicato",
        "pt": "Estilo aplicado",
        "pl": "Styl zastosowano",
        "tr": "Stil uygulandı",
        "uk": "Стиль застосовано",
        "ar": "تم تطبيق النمط",
        "zh": "样式已应用",
        "kk": "Стиль қолданылды",
        "tg": "Услуб татбиқ шуд",
        "uz": "Uslub qo‘llandi",
    },
)

register_text(
    "subtitles",
    {
        "ru": "субтитры",
        "en": "subtitles",
        "es": "subtítulos",
        "fr": "sous-titres",
        "de": "untertitel",
        "it": "sottotitoli",
        "pt": "legendas",
        "pl": "napisy",
        "tr": "altyazılar",
        "uk": "субтитри",
        "ar": "ترجمات",
        "zh": "字幕",
        "kk": "субтитр",
        "tg": "субтитрҳо",
        "uz": "subtitrlari",
    },
)

register_text(
    "translate",
    {
        "ru": "перевод",
        "en": "translate",
        "es": "traducción",
        "fr": "traduire",
        "de": "übersetzen",
        "it": "traduci",
        "pt": "tradução",
        "pl": "tłumaczenie",
        "tr": "çeviri",
        "uk": "переклад",
        "ar": "ترجمة",
        "zh": "翻译",
        "kk": "аударма",
        "tg": "тарҷума",
        "uz": "tarjima",
    },
)

register_text(
    "This video exceeds the Free limit. Upgrade to PRO for up to 10 minutes without watermark.",
    {
        "ru": "Этот ролик длиннее лимита Free. Оформи PRO для до 10 мин без водяного знака.",
        "en": "This video exceeds the Free limit. Upgrade to PRO for up to 10 minutes without watermark.",
        "es": "Este video supera el límite Free. Pásate a PRO para hasta 10 minutos sin marca de agua.",
        "fr": "Cette vidéo dépasse la limite Free. Passez à PRO pour jusqu’à 10 minutes sans filigrane.",
        "de": "Dieses Video überschreitet das Free-Limit. Upgrade auf PRO für bis zu 10 Minuten ohne Wasserzeichen.",
        "it": "Questo video supera il limite Free. Passa a PRO per fino a 10 minuti senza watermark.",
        "pt": "Este vídeo excede o limite Free. Faça upgrade para PRO para até 10 min sem marca d’água.",
        "pl": "To wideo przekracza limit Free. Przejdź na PRO, aby mieć do 10 minut bez znaku wodnego.",
        "tr": "Bu video Free limitini aşıyor. 10 dakikaya kadar filigransız kullanım için PRO’ya geç.",
        "uk": "Це відео перевищує ліміт Free. Оформи PRO, щоб отримати до 10 хв без водяного знака.",
        "ar": "هذا الفيديو يتجاوز حد باقة Free. انتقل إلى PRO للحصول على ما يصل إلى 10 دقائق بدون علامة مائية.",
        "zh": "该视频超过 Free 限制。升级到 PRO 可享受最长 10 分钟无水印。",
        "kk": "Бұл видео Free шегінен асып тұр. PRO-ға өтіп, 10 минутқа дейін сутаңбасыз алыңыз.",
        "tg": "Ин видео аз лимити Free бештар аст. Ба PRO гузаред, то то 10 дақиқа бе тамға бошед.",
        "uz": "Bu video Free limitidan oshib ketgan. 10 daqiqagacha suv belgisisiz uchun PRO ga o‘ting.",
    },
)

register_text(
    "Unknown purchase type",
    {
        "ru": "Неизвестный тип покупки",
        "en": "Unknown purchase type",
        "es": "Tipo de compra desconocido",
        "fr": "Type d’achat inconnu",
        "de": "Unbekannter Kauf-Typ",
        "it": "Tipo di acquisto sconosciuto",
        "pt": "Tipo de compra desconhecido",
        "pl": "Nieznany typ zakupu",
        "tr": "Bilinmeyen satın alma türü",
        "uk": "Невідомий тип покупки",
        "ar": "نوع شراء غير معروف",
        "zh": "未知的购买类型",
        "kk": "Белгісіз сатып алу түрі",
        "tg": "Намуди харид номаълум",
        "uz": "Noma’lum xarid turi",
    },
)

register_text(
    "⚙️ Advanced options",
    {
        "ru": "⚙️ Расширенные опции",
        "en": "⚙️ Advanced options",
        "es": "⚙️ Opciones avanzadas",
        "fr": "⚙️ Options avancées",
        "de": "⚙️ Erweiterte Optionen",
        "it": "⚙️ Opzioni avanzate",
        "pt": "⚙️ Opções avançadas",
        "pl": "⚙️ Opcje zaawansowane",
        "tr": "⚙️ Gelişmiş seçenekler",
        "uk": "⚙️ Розширені опції",
        "ar": "⚙️ خيارات متقدمة",
        "zh": "⚙️ 高级选项",
        "kk": "⚙️ Кеңейтілген параметрлер",
        "tg": "⚙️ Танзимоти пешрафта",
        "uz": "⚙️ Kengaytirilgan parametrlar",
    },
)

register_text(
    "Pick processing options:",
    {
        "ru": "Выберите опции обработки:",
        "en": "Pick processing options:",
        "es": "Elige opciones de procesamiento:",
        "fr": "Choisissez les options de traitement :",
        "de": "Wähle Verarbeitungsoptionen:",
        "it": "Scegli le opzioni di elaborazione:",
        "pt": "Escolha as opções de processamento:",
        "pl": "Wybierz opcje przetwarzania:",
        "tr": "İşleme seçeneklerini seçin:",
        "uk": "Обери опції обробки:",
        "ar": "اختر خيارات المعالجة:",
        "zh": "选择处理选项：",
        "kk": "Өңдеу опцияларын таңдаңыз:",
        "tg": "Имконоти коркардро интихоб кунед:",
        "uz": "Qayta ishlash parametrlarini tanlang:",
    },
)

register_text(
    "🔓 Upgrade to PRO",
    {
        "ru": "🔓 Оформить PRO",
        "en": "🔓 Upgrade to PRO",
        "es": "🔓 Pasar a PRO",
        "fr": "🔓 Passer en PRO",
        "de": "🔓 Auf PRO upgraden",
        "it": "🔓 Passa a PRO",
        "pt": "🔓 Fazer upgrade para PRO",
        "pl": "🔓 Przejdź na PRO",
        "tr": "🔓 PRO’ya yükselt",
        "uk": "🔓 Перейти на PRO",
        "ar": "🔓 الترقية إلى PRO",
        "zh": "🔓 升级到 PRO",
        "kk": "🔓 PRO-ға көшу",
        "tg": "🔓 Ба PRO навсозӣ кунед",
        "uz": "🔓 PRO ga yangilang",
    },
)

register_text(
    "🎛️ Options\n- Subtitles: on\n- Translate: off\n- Voiceover: off\n- Format: original\n- Style: Sub/36px/Outline1",
    {
        "ru": "🎛️ Опции\n- Субтитры: вкл\n- Перевод: выкл\n- Озвучка: выкл\n- Формат: исходный\n- Стиль: Sub/36px/Outline1",
        "en": "🎛️ Options\n- Subtitles: on\n- Translate: off\n- Voiceover: off\n- Format: original\n- Style: Sub/36px/Outline1",
        "es": "🎛️ Opciones\n- Subtítulos: activado\n- Traducción: desactivada\n- Voz en off: desactivada\n- Formato: original\n- Estilo: Sub/36px/Outline1",
        "fr": "🎛️ Options\n- Sous-titres : activés\n- Traduction : désactivée\n- Voix off : désactivée\n- Format : original\n- Style : Sub/36px/Outline1",
        "de": "🎛️ Optionen\n- Untertitel: an\n- Übersetzung: aus\n- Voiceover: aus\n- Format: original\n- Stil: Sub/36px/Outline1",
        "it": "🎛️ Opzioni\n- Sottotitoli: attivi\n- Traduzione: disattiva\n- Voce: disattiva\n- Formato: originale\n- Stile: Sub/36px/Outline1",
        "pt": "🎛️ Opções\n- Legendas: ativadas\n- Tradução: desativada\n- Narração: desativada\n- Formato: original\n- Estilo: Sub/36px/Outline1",
        "pl": "🎛️ Opcje\n- Napisy: włączone\n- Tłumaczenie: wyłączone\n- Lektor: wyłączony\n- Format: oryginalny\n- Styl: Sub/36px/Outline1",
        "tr": "🎛️ Seçenekler\n- Altyazı: açık\n- Çeviri: kapalı\n- Seslendirme: kapalı\n- Format: orijinal\n- Stil: Sub/36px/Outline1",
        "uk": "🎛️ Опції\n- Субтитри: увімкнено\n- Переклад: вимкнено\n- Озвучка: вимкнено\n- Формат: оригінал\n- Стиль: Sub/36px/Outline1",
        "ar": "🎛️ الخيارات\n- الترجمة النصية: مفعّلة\n- الترجمة: متوقفة\n- الدبلجة: متوقفة\n- التنسيق: أصلي\n- النمط: Sub/36px/Outline1",
        "zh": "🎛️ 选项\n- 字幕：开启\n- 翻译：关闭\n- 配音：关闭\n- 格式：原始\n- 样式：Sub/36px/Outline1",
        "kk": "🎛️ Параметрлер\n- Субтитр: қосулы\n- Аударма: өшірулі\n- Дыбыстау: өшірулі\n- Пішім: бастапқы\n- Стиль: Sub/36px/Outline1",
        "tg": "🎛️ Танзимот\n- Субтитр: фаъол\n- Тарҷума: ғайрифаъол\n- Озвучонӣ: ғайрифаъол\n- Формат: аслӣ\n- Услуб: Sub/36px/Outline1",
        "uz": "🎛️ Parametrlar\n- Subtitrlari: yoqilgan\n- Tarjima: o‘chirilgan\n- Ovozlanti rish: o‘chirilgan\n- Format: asl\n- Uslub: Sub/36px/Outline1",
    },
)

register_text(
    "🎬 <b>One-time processing</b>\n\nChoose video length:\n• Up to 3 min - 29₽\n• Up to 10 min - 49₽\n• Up to 30 min - 59₽\n\nAfter payment you can process one video with the selected duration.",
    {
        "ru": "🎬 <b>Разовая обработка</b>\n\nВыбери длину ролика:\n• До 3 мин — 29₽\n• До 10 мин — 49₽\n• До 30 мин — 59₽\n\nПосле оплаты можно обработать один ролик выбранной длины.",
        "en": "🎬 <b>One-time processing</b>\n\nChoose video length:\n• Up to 3 min - 29₽\n• Up to 10 min - 49₽\n• Up to 30 min - 59₽\n\nAfter payment you can process one video with the selected duration.",
        "es": "🎬 <b>Procesamiento puntual</b>\n\nElige duración:\n• Hasta 3 min - 29₽\n• Hasta 10 min - 49₽\n• Hasta 30 min - 59₽\n\nTras el pago podrás procesar un video con la duración elegida.",
        "fr": "🎬 <b>Traitement à l’unité</b>\n\nChoisissez la durée :\n• Jusqu’à 3 min - 29₽\n• Jusqu’à 10 min - 49₽\n• Jusqu’à 30 min - 59₽\n\nAprès paiement vous pourrez traiter une vidéo de la durée choisie.",
        "de": "🎬 <b>Einmalige Verarbeitung</b>\n\nWähle die Videolänge:\n• Bis 3 Min - 29₽\n• Bis 10 Min - 49₽\n• Bis 30 Min - 59₽\n\nNach der Zahlung kannst du ein Video mit dieser Länge verarbeiten.",
        "it": "🎬 <b>Elaborazione una tantum</b>\n\nScegli la durata:\n• Fino a 3 min - 29₽\n• Fino a 10 min - 49₽\n• Fino a 30 min - 59₽\n\nDopo il pagamento potrai elaborare un video della durata scelta.",
        "pt": "🎬 <b>Processamento avulso</b>\n\nEscolha a duração:\n• Até 3 min - 29₽\n• Até 10 min - 49₽\n• Até 30 min - 59₽\n\nApós o pagamento você poderá processar um vídeo com essa duração.",
        "pl": "🎬 <b>Jednorazowe przetwarzanie</b>\n\nWybierz długość wideo:\n• Do 3 min - 29₽\n• Do 10 min - 49₽\n• Do 30 min - 59₽\n\nPo płatności możesz przetworzyć jedno wideo o wybranej długości.",
        "tr": "🎬 <b>Tek seferlik işlem</b>\n\nVideo süresini seç:\n• 3 dakikaya kadar - 29₽\n• 10 dakikaya kadar - 49₽\n• 30 dakikaya kadar - 59₽\n\nÖdeme sonrası seçilen süreyle bir video işleyebilirsin.",
        "uk": "🎬 <b>Разова обробка</b>\n\nОберіть тривалість:\n• До 3 хв — 29₽\n• До 10 хв — 49₽\n• До 30 хв — 59₽\n\nПісля оплати можна обробити один ролик обраної довжини.",
        "ar": "🎬 <b>معالجة لمرة واحدة</b>\n\nاختر مدة الفيديو:\n• حتى 3 دقائق - 29₽\n• حتى 10 دقائق - 49₽\n• حتى 30 دقيقة - 59₽\n\nبعد الدفع يمكنك معالجة فيديو واحد بالمدة المحددة.",
        "zh": "🎬 <b>一次性处理</b>\n\n选择视频长度：\n• 最长 3 分钟 - 29₽\n• 最长 10 分钟 - 49₽\n• 最长 30 分钟 - 59₽\n\n付款后即可处理一段所选时长的视频。",
        "kk": "🎬 <b>Бір реттік өңдеу</b>\n\nВидео ұзындығын таңдаңыз:\n• 3 мин дейін - 29₽\n• 10 мин дейін - 49₽\n• 30 мин дейін - 59₽\n\nТөлемнен кейін таңдалған ұзындықтағы бір бейнені өңдей аласыз.",
        "tg": "🎬 <b>Коркарди якдафъаина</b>\n\nДарозии видео интихоб кунед:\n• То 3 дақ - 29₽\n• То 10 дақ - 49₽\n• То 30 дақ - 59₽\n\nПас аз пардохт метавонед як видео бо ин дарозӣ коркард кунед.",
        "uz": "🎬 <b>Bir martalik ishlov</b>\n\nVideo davomiyligini tanlang:\n• 3 daqiqagacha - 29₽\n• 10 daqiqagacha - 49₽\n• 30 daqiqagacha - 59₽\n\nTo‘lovdan so‘ng shu davomiylikdagi bitta videoni qayta ishlashingiz mumkin.",
    },
)

register_text(
    "💳 Plan\n\nFree - up to 60 sec, 720p, 3 tasks/day, watermark\nPRO 199 ₽/mo - up to 10 min, 1080p, no watermark, priority\nCREATOR 499 ₽/mo - up to 30 min, presets & voiceover",
    {
        "ru": "💳 План\n\nFree — до 60 сек, 720p, 3 задачи/день, водяной знак\nPRO 199 ₽/мес — до 10 мин, 1080p, без водяного знака, приоритет\nCREATOR 499 ₽/мес — до 30 мин, пресеты и озвучка",
        "en": "💳 Plan\n\nFree – up to 60 sec, 720p, 3 tasks/day, watermark\nPRO 199 ₽/mo – up to 10 min, 1080p, no watermark, priority\nCREATOR 499 ₽/mo – up to 30 min, presets & voiceover",
        "es": "💳 Plan\n\nFree – hasta 60 s, 720p, 3 tareas/día, marca de agua\nPRO 199 ₽/mes – hasta 10 min, 1080p, sin marca de agua, prioridad\nCREATOR 499 ₽/mes – hasta 30 min, presets y voz en off",
        "fr": "💳 Offre\n\nFree – jusqu’à 60 s, 720p, 3 tâches/jour, filigrane\nPRO 199 ₽/mois – jusqu’à 10 min, 1080p, sans filigrane, priorité\nCREATOR 499 ₽/mois – jusqu’à 30 min, presets et voix off",
        "de": "💳 Tarif\n\nFree – bis 60 s, 720p, 3 Aufgaben/Tag, Wasserzeichen\nPRO 199 ₽/Monat – bis 10 Min, 1080p, kein Wasserzeichen, Priorität\nCREATOR 499 ₽/Monat – bis 30 Min, Presets & Voiceover",
        "it": "💳 Piano\n\nFree – fino a 60 s, 720p, 3 attività/giorno, watermark\nPRO 199 ₽/mese – fino a 10 min, 1080p, senza watermark, priorità\nCREATOR 499 ₽/mese – fino a 30 min, preset e voiceover",
        "pt": "💳 Plano\n\nFree – até 60 s, 720p, 3 tarefas/dia, marca d’água\nPRO 199 ₽/mês – até 10 min, 1080p, sem marca d’água, prioridade\nCREATOR 499 ₽/mês – até 30 min, presets e narração",
        "pl": "💳 Plan\n\nFree – do 60 s, 720p, 3 zadania/dzień, znak wodny\nPRO 199 ₽/msc – do 10 min, 1080p, bez znaku wodnego, priorytet\nCREATOR 499 ₽/msc – do 30 min, presety i lektor",
        "tr": "💳 Plan\n\nFree – 60 sn’ye kadar, 720p, günde 3 görev, filigranlı\nPRO 199 ₽/ay – 10 dakikaya kadar, 1080p, filigransız, öncelikli\nCREATOR 499 ₽/ay – 30 dakikaya kadar, presetler ve seslendirme",
        "uk": "💳 План\n\nFree – до 60 c, 720p, 3 задачі/день, водяний знак\nPRO 199 ₽/міс – до 10 хв, 1080p, без водяного знака, пріоритет\nCREATOR 499 ₽/міс – до 30 хв, пресети та озвучка",
        "ar": "💳 الخطة\n\nFree – حتى 60 ثانية، ‎720p‎، 3 مهام/يوم، بعلامة مائية\nPRO 199 ₽/شهر – حتى 10 دقائق، ‎1080p‎، بلا علامة مائية، أولوية\nCREATOR 499 ₽/شهر – حتى 30 دقيقة، إعدادات ودبلجة",
        "zh": "💳 套餐\n\nFree – 最长 60 秒，720p，每天 3 个任务，带水印\nPRO 199 ₽/月 – 最长 10 分钟，1080p，无水印，优先级更高\nCREATOR 499 ₽/月 – 最长 30 分钟，包含预设和配音",
        "kk": "💳 Тариф\n\nFree – 60 с дейін, 720p, күніне 3 тапсырма, сутаңба\nPRO 199 ₽/ай – 10 мин дейін, 1080p, сутаңбасыз, басымдық\nCREATOR 499 ₽/ай – 30 мин дейін, пресеттер мен дыбыстау",
        "tg": "💳 Нақша\n\nFree – то 60 сония, 720p, 3 вазифа/рӯз, бо тамға\nPRO 199 ₽/моҳ – то 10 дақ, 1080p, бидуни тамға, афзалият\nCREATOR 499 ₽/моҳ – то 30 дақ, пресетҳо ва овозгузорӣ",
        "uz": "💳 Tarif\n\nFree – 60 soniyagacha, 720p, kuniga 3 ta topshiriq, suv belgili\nPRO 199 ₽/oy – 10 daqiqagacha, 1080p, suv belgisisiz, ustuvorlik\nCREATOR 499 ₽/oy – 30 daqiqagacha, presetlar va ovoz",
    },
)

register_text(
    "🧾 Recent tasks",
    {
        "ru": "🧾 Последние задачи",
        "en": "🧾 Recent tasks",
        "es": "🧾 Tareas recientes",
        "fr": "🧾 Tâches récentes",
        "de": "🧾 Letzte Aufgaben",
        "it": "🧾 Attività recenti",
        "pt": "🧾 Tarefas recentes",
        "pl": "🧾 Ostatnie zadania",
        "tr": "🧾 Son görevler",
        "uk": "🧾 Останні задачі",
        "ar": "🧾 المهام الأخيرة",
        "zh": "🧾 最近的任务",
        "kk": "🧾 Соңғы тапсырмалар",
        "tg": "🧾 Вазифаҳои охирин",
        "uz": "🧾 So‘nggi vazifalar",
    },
)

register_text(
    "🧾 Recent tasks\nNo tasks yet. Send a video to start.",
    {
        "ru": "🧾 Последние задачи\nПока пусто. Отправь видео, чтобы начать.",
        "en": "🧾 Recent tasks\nNo tasks yet. Send a video to start.",
        "es": "🧾 Tareas recientes\nAún no hay tareas. Envía un video para empezar.",
        "fr": "🧾 Tâches récentes\nAucune tâche pour le moment. Envoyez une vidéo pour commencer.",
        "de": "🧾 Letzte Aufgaben\nNoch keine Aufgaben. Sende ein Video, um zu starten.",
        "it": "🧾 Attività recenti\nAncora nessuna attività. Invia un video per iniziare.",
        "pt": "🧾 Tarefas recentes\nAinda não há tarefas. Envie um vídeo para começar.",
        "pl": "🧾 Ostatnie zadania\nBrak zadań. Wyślij wideo, aby zacząć.",
        "tr": "🧾 Son görevler\nHenüz görev yok. Başlamak için video gönder.",
        "uk": "🧾 Останні задачі\nПоки пусто. Надішли відео, щоб почати.",
        "ar": "🧾 المهام الأخيرة\nلا مهام بعد. أرسل فيديو للبدء.",
        "zh": "🧾 最近的任务\n暂无任务。发送视频开始。",
        "kk": "🧾 Соңғы тапсырмалар\nӘзірге жоқ. Бастау үшін бейне жіберіңіз.",
        "tg": "🧾 Вазифаҳои охирин\nҲанӯз вазифае нест. Барои оғоз видео фиристед.",
        "uz": "🧾 So‘nggi vazifalar\nHozircha vazifa yo‘q. Boshlash uchun video yuboring.",
    },
)

register_text(
    "🚀 Task #{task.id} created\n\nOptions: subtitles {subs} · translate {trn} · voiceover {tts} · 9:16 {fmt}\n\nEstimated time: ~1–2 min",
    {
        "ru": "🚀 Задача #{task.id} создана\n\nОпции: субтитры {subs} · перевод {trn} · озвучка {tts} · 9:16 {fmt}\n\nОценка времени: ~1–2 мин",
        "en": "🚀 Task #{task.id} created\n\nOptions: subtitles {subs} · translate {trn} · voiceover {tts} · 9:16 {fmt}\n\nEstimated time: ~1–2 min",
        "es": "🚀 Tarea #{task.id} creada\n\nOpciones: subtítulos {subs} · traducir {trn} · voz {tts} · 9:16 {fmt}\n\nTiempo estimado: ~1–2 min",
        "fr": "🚀 Tâche #{task.id} créée\n\nOptions : sous-titres {subs} · traduction {trn} · voix off {tts} · 9:16 {fmt}\n\nTemps estimé : ~1–2 min",
        "de": "🚀 Aufgabe #{task.id} erstellt\n\nOptionen: Untertitel {subs} · Übersetzung {trn} · Voiceover {tts} · 9:16 {fmt}\n\nGeschätzte Zeit: ~1–2 Min",
        "it": "🚀 Task #{task.id} creata\n\nOpzioni: sottotitoli {subs} · traduzione {trn} · voiceover {tts} · 9:16 {fmt}\n\nTempo stimato: ~1–2 min",
        "pt": "🚀 Tarefa #{task.id} criada\n\nOpções: legendas {subs} · tradução {trn} · narração {tts} · 9:16 {fmt}\n\nTempo estimado: ~1–2 min",
        "pl": "🚀 Zadanie #{task.id} utworzone\n\nOpcje: napisy {subs} · tłumaczenie {trn} · lektor {tts} · 9:16 {fmt}\n\nSzacowany czas: ~1–2 min",
        "tr": "🚀 Görev #{task.id} oluşturuldu\n\nSeçenekler: altyazı {subs} · çeviri {trn} · seslendirme {tts} · 9:16 {fmt}\n\nTahmini süre: ~1–2 dk",
        "uk": "🚀 Завдання #{task.id} створено\n\nОпції: субтитри {subs} · переклад {trn} · озвучка {tts} · 9:16 {fmt}\n\nОрієнтовний час: ~1–2 хв",
        "ar": "🚀 تم إنشاء المهمة #{task.id}\n\nالخيارات: ترجمات {subs} · ترجمة {trn} · دبلجة {tts} · 9:16 {fmt}\n\nالوقت التقديري: ~1–2 دقيقة",
        "zh": "🚀 任务 #{task.id} 已创建\n\n选项：字幕 {subs} · 翻译 {trn} · 配音 {tts} · 9:16 {fmt}\n\n预计时间：约 1–2 分钟",
        "kk": "🚀 Тапсырма #{task.id} құрылды\n\nПараметрлер: субтитр {subs} · аударма {trn} · дыбыстау {tts} · 9:16 {fmt}\n\nБолжалды уақыт: ~1–2 мин",
        "tg": "🚀 Вазифаи #{task.id} эҷод шуд\n\nИмконот: субтитрҳо {subs} · тарҷума {trn} · овоз {tts} · 9:16 {fmt}\n\nВақти тахминӣ: ~1–2 дақ",
        "uz": "🚀 Vazifa #{task.id} yaratildi\n\nParametrlar: subtitrlar {subs} · tarjima {trn} · ovoz {tts} · 9:16 {fmt}\n\nTaxminiy vaqt: ~1–2 daqiqa",
    },
)

register_text(
    "✅ File received and queued!\n\nTask #{task.id}. ⏳ Processing started.\nDefaults: subtitles on, translate/voiceover/vertical off.",
    {
        "ru": "✅ Файл получен и поставлен в очередь!\n\nЗадача #{task.id}. ⏳ Обработка началась.\nПо умолчанию: субтитры вкл, перевод/озвучка/вертикальный формат — выкл.",
        "en": "✅ File received and queued!\n\nTask #{task.id}. ⏳ Processing started.\nDefaults: subtitles on, translate/voiceover/vertical off.",
        "es": "✅ Archivo recibido y en cola.\n\nTarea #{task.id}. ⏳ Procesamiento iniciado.\nPor defecto: subtítulos activados, traducción/voz/formato vertical desactivados.",
        "fr": "✅ Fichier reçu et en file d’attente.\n\nTâche #{task.id}. ⏳ Traitement lancé.\nPar défaut : sous-titres activés, traduction/voix/off vertical désactivés.",
        "de": "✅ Datei empfangen und in die Warteschlange gestellt!\n\nAufgabe #{task.id}. ⏳ Verarbeitung gestartet.\nStandard: Untertitel an, Übersetzung/Voiceover/Hochformat aus.",
        "it": "✅ File ricevuto e messo in coda!\n\nTask #{task.id}. ⏳ Elaborazione avviata.\nDefault: sottotitoli attivi, traduzione/voiceover/verticale disattivati.",
        "pt": "✅ Arquivo recebido e enfileirado!\n\nTarefa #{task.id}. ⏳ Processamento iniciado.\nPadrões: legendas ativas, tradução/narração/formato vertical desativados.",
        "pl": "✅ Plik odebrany i dodany do kolejki!\n\nZadanie #{task.id}. ⏳ Przetwarzanie rozpoczęte.\nDomyślnie: napisy włączone, tłumaczenie/lektor/pionowy wyłączone.",
        "tr": "✅ Dosya alındı ve kuyruğa eklendi!\n\nGörev #{task.id}. ⏳ İşleme başladı.\nVarsayılanlar: altyazı açık, çeviri/seslendirme/dikey kapalı.",
        "uk": "✅ Файл отримано й додано в чергу!\n\nЗавдання #{task.id}. ⏳ Обробка розпочата.\nЗа замовчуванням: субтитри вкл, переклад/озвучка/вертикальний статус викл.",
        "ar": "✅ تم استلام الملف ووضعه في قائمة الانتظار!\n\nالمهمة #{task.id}. ⏳ بدأت المعالجة.\nالافتراضات: الترجمة النصية مفعلة، الترجمة/الدبلجة/الوضع الرأسي معطلة.",
        "zh": "✅ 文件已接收并排队！\n\n任务 #{task.id}。⏳ 已开始处理。\n默认：字幕开启，翻译/配音/竖屏关闭。",
        "kk": "✅ Файл қабылданды және кезекке қойылды!\n\nТапсырма #{task.id}. ⏳ Өңдеу басталды.\nӘдепкі бойынша: субтитр қосулы, аударма/дыбыстау/тік формат өшірулі.",
        "tg": "✅ Файл қабул шуда ба навбат гузошта шуд!\n\nВазифа #{task.id}. ⏳ Коркард оғоз шуд.\nПешфарз: субтитрҳо фаъол, тарҷума/овоз/формати амудӣ ғайрифаъол.",
        "uz": "✅ Fayl qabul qilindi va navbatga qo‘yildi!\n\nVazifa #{task.id}. ⏳ Qayta ishlash boshlandi.\nStandart: subtitrlar yoqilgan, tarjima/ovoz/vertikal o‘chirilgan.",
    },
)

register_text(
    "✅ Task #{task.id} queued!\n\n⏳ Processing may take a few minutes.\nWe will send the result when it’s done.",
    {
        "ru": "✅ Задача #{task.id} поставлена в очередь!\n\n⏳ Обработка может занять несколько минут.\nМы отправим результат, когда всё будет готово.",
        "en": "✅ Task #{task.id} queued!\n\n⏳ Processing may take a few minutes.\nWe will send the result when it’s done.",
        "es": "✅ Tarea #{task.id} en cola.\n\n⏳ El procesamiento puede tardar unos minutos.\nTe enviaremos el resultado al finalizar.",
        "fr": "✅ Tâche #{task.id} en file d’attente.\n\n⏳ Le traitement peut prendre quelques minutes.\nNous enverrons le résultat une fois terminé.",
        "de": "✅ Aufgabe #{task.id} in der Warteschlange!\n\n⏳ Die Verarbeitung kann einige Minuten dauern.\nWir senden das Ergebnis, sobald es fertig ist.",
        "it": "✅ Task #{task.id} in coda!\n\n⏳ L’elaborazione può richiedere alcuni minuti.\nTi invieremo il risultato appena pronto.",
        "pt": "✅ Tarefa #{task.id} na fila!\n\n⏳ O processamento pode levar alguns minutos.\nEnviaremos o resultado quando terminar.",
        "pl": "✅ Zadanie #{task.id} w kolejce!\n\n⏳ Przetwarzanie może potrwać kilka minut.\nPrześlemy wynik, gdy będzie gotowy.",
        "tr": "✅ Görev #{task.id} kuyruğa alındı!\n\n⏳ İşleme birkaç dakika sürebilir.\nBittiğinde sonucu göndereceğiz.",
        "uk": "✅ Завдання #{task.id} в черзі!\n\n⏳ Обробка може тривати кілька хвилин.\nМи надішлемо результат, коли все завершиться.",
        "ar": "✅ تم إدراج المهمة #{task.id} في قائمة الانتظار!\n\n⏳ قد يستغرق المعالجة بضع دقائق.\nسنرسل النتيجة عند الانتهاء.",
        "zh": "✅ 任务 #{task.id} 已排队！\n\n⏳ 处理可能需要几分钟。\n完成后我们会发送结果。",
        "kk": "✅ Тапсырма #{task.id} кезекте!\n\n⏳ Өңдеу бірнеше минут алуы мүмкін.\nДайын болғанда нәтижені жібереміз.",
        "tg": "✅ Вазифаи #{task.id} ба навбат гузошта шуд!\n\n⏳ Коркард метавонад чанд дақиқа тӯл кашад.\nНатиҷаро пас аз анҷом мефиристем.",
        "uz": "✅ Vazifa #{task.id} navbatga qo‘yildi!\n\n⏳ Qayta ishlash bir necha daqiqa davom etishi mumkin.\nTugagach natijani yuboramiz.",
    },
)

register_text(
    "❌ Failed to create task: {error}\n\nPlease try again later or contact support.",
    {
        "ru": "❌ Ошибка при создании задачи: {error}\n\nПопробуйте позже или обратитесь в поддержку.",
        "en": "❌ Failed to create task: {error}\n\nPlease try again later or contact support.",
        "es": "❌ Error al crear la tarea: {error}\n\nInténtalo más tarde o contacta con soporte.",
        "fr": "❌ Échec de création de la tâche : {error}\n\nRéessayez plus tard ou contactez l’assistance.",
        "de": "❌ Fehler beim Erstellen der Aufgabe: {error}\n\nBitte später erneut versuchen oder den Support kontaktieren.",
        "it": "❌ Errore nella creazione della task: {error}\n\nRiprova più tardi o contatta il supporto.",
        "pt": "❌ Falha ao criar a tarefa: {error}\n\nTente novamente mais tarde ou contate o suporte.",
        "pl": "❌ Błąd tworzenia zadania: {error}\n\nSpróbuj ponownie później lub skontaktuj się z pomocą.",
        "tr": "❌ Görev oluşturulamadı: {error}\n\nLütfen daha sonra tekrar deneyin veya destekle iletişime geçin.",
        "uk": "❌ Не вдалося створити задачу: {error}\n\nСпробуйте пізніше або зверніться в підтримку.",
        "ar": "❌ فشل إنشاء المهمة: {error}\n\nحاول مرة أخرى لاحقًا أو تواصل مع الدعم.",
        "zh": "❌ 创建任务失败：{error}\n\n请稍后重试或联系支持。",
        "kk": "❌ Тапсырма жасау қателігі: {error}\n\nКейінірек қайталап көріңіз немесе қолдауға жүгініңіз.",
        "tg": "❌ Ҳангоми эҷоди вазифа хато: {error}\n\nБаъдтар боз кӯшиш кунед ё ба дастгирӣ муроҷиат кунед.",
        "uz": "❌ Vazifa yaratishda xatolik: {error}\n\nKeyinroq qayta urinib ko‘ring yoki yordamga murojaat qiling.",
    },
)

register_text(
    "❌ Failed to create task: {error}\n\nTry again later or contact support.",
    {
        "ru": "❌ Ошибка при создании задачи: {error}\n\nПопробуйте позже или обратитесь в поддержку.",
        "en": "❌ Failed to create task: {error}\n\nTry again later or contact support.",
        "es": "❌ Error al crear la tarea: {error}\n\nInténtalo más tarde o contacta con soporte.",
        "fr": "❌ Échec de création de la tâche : {error}\n\nRéessayez plus tard ou contactez l’assistance.",
        "de": "❌ Fehler beim Erstellen der Aufgabe: {error}\n\nVersuche es später erneut oder kontaktiere den Support.",
        "it": "❌ Errore nella creazione della task: {error}\n\nRiprova più tardi o contatta il supporto.",
        "pt": "❌ Falha ao criar a tarefa: {error}\n\nTente novamente mais tarde ou contate o suporte.",
        "pl": "❌ Błąd tworzenia zadania: {error}\n\nSpróbuj ponownie później lub skontaktuj się z pomocą.",
        "tr": "❌ Görev oluşturulamadı: {error}\n\nDaha sonra tekrar deneyin veya destekle iletişime geçin.",
        "uk": "❌ Не вдалося створити задачу: {error}\n\nСпробуйте пізніше або зверніться в підтримку.",
        "ar": "❌ فشل إنشاء المهمة: {error}\n\nحاول مرة أخرى لاحقًا أو تواصل مع الدعم.",
        "zh": "❌ 创建任务失败：{error}\n\n请稍后重试或联系支持。",
        "kk": "❌ Тапсырма жасау қателігі: {error}\n\nКейінірек қайталап көріңіз немесе қолдауға жүгініңіз.",
        "tg": "❌ Ҳангоми эҷоди вазифа хато: {error}\n\nБаъдтар боз кӯшиш кунед ё ба дастгирӣ муроҷиат кунед.",
        "uz": "❌ Vazifa yaratishda xatolik: {error}\n\nKeyinroq qayta urinib ko‘ring yoki yordamga murojaat qiling.",
    },
)

register_text(
    "❌ Failed to create payment: {error}",
    {
        "ru": "❌ Ошибка при создании платежа: {error}",
        "en": "❌ Failed to create payment: {error}",
        "es": "❌ Error al crear el pago: {error}",
        "fr": "❌ Échec de création du paiement : {error}",
        "de": "❌ Fehler beim Erstellen der Zahlung: {error}",
        "it": "❌ Errore nella creazione del pagamento: {error}",
        "pt": "❌ Falha ao criar o pagamento: {error}",
        "pl": "❌ Błąd tworzenia płatności: {error}",
        "tr": "❌ Ödeme oluşturulamadı: {error}",
        "uk": "❌ Не вдалося створити платіж: {error}",
        "ar": "❌ فشل إنشاء الدفع: {error}",
        "zh": "❌ 创建付款失败：{error}",
        "kk": "❌ Төлем жасау қателігі: {error}",
        "tg": "❌ Ҳангоми сохтани пардохт хато: {error}",
        "uz": "❌ To‘lovni yaratishda xatolik: {error}",
    },
)

register_text(
    "❌ Failed to create payment: {error}\n\nTry again later or contact support.",
    {
        "ru": "❌ Ошибка при создании платежа: {error}\n\nПопробуйте позже или обратитесь в поддержку.",
        "en": "❌ Failed to create payment: {error}\n\nTry again later or contact support.",
        "es": "❌ Error al crear el pago: {error}\n\nInténtalo más tarde o contacta con soporte.",
        "fr": "❌ Échec de création du paiement : {error}\n\nRéessayez plus tard ou contactez l’assistance.",
        "de": "❌ Fehler beim Erstellen der Zahlung: {error}\n\nVersuche es später erneut oder kontaktiere den Support.",
        "it": "❌ Errore nella creazione del pagamento: {error}\n\nRiprova più tardi o contatta il supporto.",
        "pt": "❌ Falha ao criar o pagamento: {error}\n\nTente novamente mais tarde ou contate o suporte.",
        "pl": "❌ Błąd tworzenia płatności: {error}\n\nSpróbuj ponownie później lub skontaktuj się z pomocą.",
        "tr": "❌ Ödeme oluşturulamadı: {error}\n\nDaha sonra tekrar deneyin veya destekle iletişime geçin.",
        "uk": "❌ Не вдалося створити платіж: {error}\n\nСпробуйте пізніше або зверніться в підтримку.",
        "ar": "❌ فشل إنشاء الدفع: {error}\n\nحاول مرة أخرى لاحقًا أو تواصل مع الدعم.",
        "zh": "❌ 创建付款失败：{error}\n\n请稍后重试或联系支持。",
        "kk": "❌ Төлем жасау қателігі: {error}\n\nКейінірек қайталап көріңіз немесе қолдауға жүгініңіз.",
        "tg": "❌ Ҳангоми сохтани пардохт хато: {error}\n\nБаъдтар боз кӯшиш кунед ё ба дастгирӣ муроҷиат кунед.",
        "uz": "❌ To‘lovni yaratishda xatolik: {error}\n\nKeyinroq qayta urinib ko‘ring yoki yordamga murojaat qiling.",
    },
)

register_text(
    "💳 <b>Payment: {description}</b>\n\nAmount: {amount}₽\n\nOpen the link to pay:\n{payment_url}\n\nAfter successful payment your plan will activate automatically.",
    {
        "ru": "💳 <b>Платёж: {description}</b>\n\nСумма: {amount}₽\n\nПерейдите по ссылке для оплаты:\n{payment_url}\n\nПосле успешной оплаты тариф активируется автоматически.",
        "en": "💳 <b>Payment: {description}</b>\n\nAmount: {amount}₽\n\nOpen the link to pay:\n{payment_url}\n\nAfter successful payment your plan will activate automatically.",
        "es": "💳 <b>Pago: {description}</b>\n\nImporte: {amount}₽\n\nAbre el enlace para pagar:\n{payment_url}\n\nTras el pago tu plan se activará automáticamente.",
        "fr": "💳 <b>Paiement : {description}</b>\n\nMontant : {amount}₽\n\nOuvrez le lien pour payer :\n{payment_url}\n\nAprès paiement, votre offre s’activera automatiquement.",
        "de": "💳 <b>Zahlung: {description}</b>\n\nBetrag: {amount}₽\n\nÖffne den Link zur Zahlung:\n{payment_url}\n\nNach erfolgreicher Zahlung wird dein Tarif automatisch aktiviert.",
        "it": "💳 <b>Pagamento: {description}</b>\n\nImporto: {amount}₽\n\nApri il link per pagare:\n{payment_url}\n\nDopo il pagamento il piano si attiverà automaticamente.",
        "pt": "💳 <b>Pagamento: {description}</b>\n\nValor: {amount}₽\n\nAbra o link para pagar:\n{payment_url}\n\nApós o pagamento o plano será ativado automaticamente.",
        "pl": "💳 <b>Płatność: {description}</b>\n\nKwota: {amount}₽\n\nOtwórz link, aby zapłacić:\n{payment_url}\n\nPo płatności plan aktywuje się automatycznie.",
        "tr": "💳 <b>Ödeme: {description}</b>\n\nTutar: {amount}₽\n\nÖdeme için bağlantıyı açın:\n{payment_url}\n\nBaşarılı ödemeden sonra planın otomatik olarak aktive edilir.",
        "uk": "💳 <b>Платіж: {description}</b>\n\nСума: {amount}₽\n\nВідкрий посилання для оплати:\n{payment_url}\n\nПісля оплати тариф активується автоматично.",
        "ar": "💳 <b>الدفع: {description}</b>\n\nالمبلغ: {amount}₽\n\nافتح الرابط للدفع:\n{payment_url}\n\nبعد الدفع سيتم تفعيل خطتك تلقائيًا.",
        "zh": "💳 <b>付款：{description}</b>\n\n金额：{amount}₽\n\n打开链接支付：\n{payment_url}\n\n支付成功后套餐将自动激活。",
        "kk": "💳 <b>Төлем: {description}</b>\n\nСома: {amount}₽\n\nТөлеу үшін сілтемені ашыңыз:\n{payment_url}\n\nСәтті төлемнен кейін тариф автоматты түрде қосылады.",
        "tg": "💳 <b>Пардохт: {description}</b>\n\nМаблағ: {amount}₽\n\nБарои пардохт пайвандро кушоед:\n{payment_url}\n\nПас аз пардохти муваффақ нақша худкор фаъол мешавад.",
        "uz": "💳 <b>To‘lov: {description}</b>\n\nMiqdor: {amount}₽\n\nTo‘lov uchun havolani oching:\n{payment_url}\n\nTo‘lov muvaffaqiyatli bo‘lgach tarif avtomatik faollashadi.",
    },
)

register_text(
    "💳 PRO payment (199₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
    {
        "ru": "💳 Оплата PRO (199₽/мес)\nСсылка на оплату:\n{payment_url}\n\nОжидаем оплату… Нажми «🔄 Проверить статус» после оплаты.",
        "en": "💳 PRO payment (199₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
        "es": "💳 Pago PRO (199₽/mes)\nEnlace de pago:\n{payment_url}\n\nEsperando el pago… Pulsa «🔄 Verificar estado» después de pagar.",
        "fr": "💳 Paiement PRO (199₽/mois)\nLien de paiement :\n{payment_url}\n\nEn attente du paiement… Appuyez sur «🔄 Vérifier l’état» après le paiement.",
        "de": "💳 PRO-Zahlung (199₽/Monat)\nZahlungslink:\n{payment_url}\n\nWarte auf Zahlung… Drücke „🔄 Status prüfen“ nach der Zahlung.",
        "it": "💳 Pagamento PRO (199₽/mese)\nLink di pagamento:\n{payment_url}\n\nIn attesa del pagamento… Premi “🔄 Verifica stato” dopo il pagamento.",
        "pt": "💳 Pagamento PRO (199₽/mês)\nLink de pagamento:\n{payment_url}\n\nAguardando pagamento… Pressione “🔄 Verificar status” após pagar.",
        "pl": "💳 Płatność PRO (199₽/msc)\nLink do płatności:\n{payment_url}\n\nOczekiwanie na płatność… Po opłacie naciśnij „🔄 Sprawdź status”.",
        "tr": "💳 PRO ödemesi (199₽/ay)\nÖdeme bağlantısı:\n{payment_url}\n\nÖdeme bekleniyor… Ödedikten sonra “🔄 Durumu kontrol et” düğmesine bas.",
        "uk": "💳 Оплата PRO (199₽/міс)\nПосилання для оплати:\n{payment_url}\n\nОчікуємо оплату… Після оплати натисніть «🔄 Перевірити статус».",
        "ar": "💳 دفع PRO (199₽/شهر)\nرابط الدفع:\n{payment_url}\n\nبانتظار الدفع… اضغط «🔄 التحقق من الحالة» بعد الدفع.",
        "zh": "💳 PRO 付款 (199₽/月)\n付款链接：\n{payment_url}\n\n等待付款… 付款后点击“🔄 检查状态”。",
        "kk": "💳 PRO төлемі (199₽/ай)\nТөлем сілтемесі:\n{payment_url}\n\nТөлем күтілуде… Төлемнен кейін «🔄 Күйін тексеру» батырмасын басыңыз.",
        "tg": "💳 Пардохти PRO (199₽/моҳ)\nПайванди пардохт:\n{payment_url}\n\nПардохтро интизорем… Пас аз пардохт «🔄 Санҷиши ҳолат»-ро пахш кунед.",
        "uz": "💳 PRO to‘lovi (199₽/oy)\nTo‘lov havolasi:\n{payment_url}\n\nTo‘lov kutilmoqda… To‘lovdan so‘ng “🔄 Holatni tekshirish” tugmasini bosing.",
    },
)

register_text(
    "💳 CREATOR payment (499₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
    {
        "ru": "💳 Оплата CREATOR (499₽/мес)\nСсылка на оплату:\n{payment_url}\n\nОжидаем оплату… Нажми «🔄 Проверить статус» после оплаты.",
        "en": "💳 CREATOR payment (499₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
        "es": "💳 Pago CREATOR (499₽/mes)\nEnlace de pago:\n{payment_url}\n\nEsperando el pago… Pulsa «🔄 Verificar estado» después de pagar.",
        "fr": "💳 Paiement CREATOR (499₽/mois)\nLien de paiement :\n{payment_url}\n\nEn attente du paiement… Appuyez sur «🔄 Vérifier l’état» après le paiement.",
        "de": "💳 CREATOR-Zahlung (499₽/Monat)\nZahlungslink:\n{payment_url}\n\nWarte auf Zahlung… Drücke „🔄 Status prüfen“ nach der Zahlung.",
        "it": "💳 Pagamento CREATOR (499₽/mese)\nLink di pagamento:\n{payment_url}\n\nIn attesa del pagamento… Premi “🔄 Verifica stato” dopo il pagamento.",
        "pt": "💳 Pagamento CREATOR (499₽/mês)\nLink de pagamento:\n{payment_url}\n\nAguardando pagamento… Pressione “🔄 Verificar status” após pagar.",
        "pl": "💳 Płatność CREATOR (499₽/msc)\nLink do płatności:\n{payment_url}\n\nOczekiwanie na płatność… Po opłacie naciśnij „🔄 Sprawdź status”.",
        "tr": "💳 CREATOR ödemesi (499₽/ay)\nÖdeme bağlantısı:\n{payment_url}\n\nÖdeme bekleniyor… Ödedikten sonra “🔄 Durumu kontrol et” düğmesine bas.",
        "uk": "💳 Оплата CREATOR (499₽/міс)\nПосилання для оплати:\n{payment_url}\n\nОчікуємо оплату… Після оплати натисніть «🔄 Перевірити статус».",
        "ar": "💳 دفع CREATOR (499₽/شهر)\nرابط الدفع:\n{payment_url}\n\nبانتظار الدفع… اضغط «🔄 التحقق من الحالة» بعد الدفع.",
        "zh": "💳 CREATOR 付款 (499₽/月)\n付款链接：\n{payment_url}\n\n等待付款… 付款后点击“🔄 检查状态”。",
        "kk": "💳 CREATOR төлемі (499₽/ай)\nТөлем сілтемесі:\n{payment_url}\n\nТөлем күтілуде… Төлемнен кейін «🔄 Күйін тексеру» батырмасын басыңыз.",
        "tg": "💳 Пардохти CREATOR (499₽/моҳ)\nПайванди пардохт:\n{payment_url}\n\nПардохтро интизорем… Пас аз пардохт «🔄 Санҷиши ҳолат»-ро пахш кунед.",
        "uz": "💳 CREATOR to‘lovi (499₽/oy)\nTo‘lov havolasi:\n{payment_url}\n\nTo‘lov kutilmoqda… To‘lovdan so‘ng “🔄 Holatni tekshirish” tugmasini bosing.",
    },
)

register_key(
    "profile.status_until",
    {
        "ru": "до {date}",
        "en": "until {date}",
        "es": "hasta {date}",
        "fr": "jusqu’au {date}",
        "de": "bis {date}",
        "it": "fino al {date}",
        "pt": "até {date}",
        "pl": "do {date}",
        "tr": "{date} tarihine kadar",
        "uk": "до {date}",
        "ar": "حتى {date}",
        "zh": "至 {date}",
        "kk": "{date} дейін",
        "tg": "то {date}",
        "uz": "{date} gacha",
    },
)

register_key(
    "profile.status_permanent",
    {
        "ru": "бессрочно",
        "en": "permanent",
        "es": "permanente",
        "fr": "permanent",
        "de": "dauerhaft",
        "it": "permanente",
        "pt": "permanente",
        "pl": "bezterminowo",
        "tr": "süresiz",
        "uk": "безстроково",
        "ar": "دائم",
        "zh": "永久",
        "kk": "мерзімсіз",
        "tg": "бемуҳлат",
        "uz": "doimiy",
    },
)

register_key(
    "profile.status_inactive",
    {
        "ru": "не активна",
        "en": "inactive",
        "es": "inactiva",
        "fr": "inactive",
        "de": "inaktiv",
        "it": "non attivo",
        "pt": "inativo",
        "pl": "nieaktywna",
        "tr": "pasif",
        "uk": "неактивна",
        "ar": "غير نشط",
        "zh": "未激活",
        "kk": "белсенді емес",
        "tg": "ғайрифаъол",
        "uz": "faol emas",
    },
)

register_key(
    "profile.boolean_yes",
    {
        "ru": "Да",
        "en": "Yes",
        "es": "Sí",
        "fr": "Oui",
        "de": "Ja",
        "it": "Sì",
        "pt": "Sim",
        "pl": "Tak",
        "tr": "Evet",
        "uk": "Так",
        "ar": "نعم",
        "zh": "是",
        "kk": "Иә",
        "tg": "Бале",
        "uz": "Ha",
    },
)

register_key(
    "profile.boolean_no",
    {
        "ru": "Нет",
        "en": "No",
        "es": "No",
        "fr": "Non",
        "de": "Nein",
        "it": "No",
        "pt": "Não",
        "pl": "Nie",
        "tr": "Hayır",
        "uk": "Ні",
        "ar": "لا",
        "zh": "否",
        "kk": "Жоқ",
        "tg": "Не",
        "uz": "Yo‘q",
    },
)

register_key(
    "profile.summary",
    {
        "ru": "👤 <b>Ваш профиль</b>\n\n<b>Тариф:</b> {tier} ({status})\n<b>Задач сегодня:</b> {today}/{daily}\n<b>Всего обработано:</b> {total}\n\n<b>Лимиты тарифа:</b>\n• Макс. длительность: {max_duration} сек\n• Качество: до {max_quality}\n• Водяной знак: {watermark}\n• Задач в день: {daily}\n\n💎 Используйте /pricing для улучшения тарифа",
        "en": "👤 <b>Your profile</b>\n\n<b>Plan:</b> {tier} ({status})\n<b>Tasks today:</b> {today}/{daily}\n<b>Total processed:</b> {total}\n\n<b>Plan limits:</b>\n• Max duration: {max_duration} sec\n• Quality: up to {max_quality}\n• Watermark: {watermark}\n• Tasks per day: {daily}\n\n💎 Use /pricing to upgrade",
        "es": "👤 <b>Tu perfil</b>\n\n<b>Plan:</b> {tier} ({status})\n<b>Tareas hoy:</b> {today}/{daily}\n<b>Total procesado:</b> {total}\n\n<b>Límites del plan:</b>\n• Duración máx.: {max_duration} s\n• Calidad: hasta {max_quality}\n• Marca de agua: {watermark}\n• Tareas por día: {daily}\n\n💎 Usa /pricing para mejorar",
        "fr": "👤 <b>Votre profil</b>\n\n<b>Offre :</b> {tier} ({status})\n<b>Tâches aujourd’hui :</b> {today}/{daily}\n<b>Total traité :</b> {total}\n\n<b>Limites de l’offre :</b>\n• Durée max : {max_duration} s\n• Qualité : jusqu’à {max_quality}\n• Filigrane : {watermark}\n• Tâches par jour : {daily}\n\n💎 Utilisez /pricing pour mettre à niveau",
        "de": "👤 <b>Dein Profil</b>\n\n<b>Tarif:</b> {tier} ({status})\n<b>Aufgaben heute:</b> {today}/{daily}\n<b>Insgesamt verarbeitet:</b> {total}\n\n<b>Tariflimits:</b>\n• Max. Dauer: {max_duration} s\n• Qualität: bis {max_quality}\n• Wasserzeichen: {watermark}\n• Aufgaben pro Tag: {daily}\n\n💎 Nutze /pricing, um upzugraden",
        "it": "👤 <b>Il tuo profilo</b>\n\n<b>Piano:</b> {tier} ({status})\n<b>Task oggi:</b> {today}/{daily}\n<b>Totale elaborati:</b> {total}\n\n<b>Limiti del piano:</b>\n• Durata max: {max_duration} s\n• Qualità: fino a {max_quality}\n• Watermark: {watermark}\n• Task al giorno: {daily}\n\n💎 Usa /pricing per fare upgrade",
        "pt": "👤 <b>Seu perfil</b>\n\n<b>Plano:</b> {tier} ({status})\n<b>Tarefas hoje:</b> {today}/{daily}\n<b>Total processado:</b> {total}\n\n<b>Limites do plano:</b>\n• Duração máx.: {max_duration} s\n• Qualidade: até {max_quality}\n• Marca d’água: {watermark}\n• Tarefas por dia: {daily}\n\n💎 Use /pricing para fazer upgrade",
        "pl": "👤 <b>Twój profil</b>\n\n<b>Plan:</b> {tier} ({status})\n<b>Zadań dziś:</b> {today}/{daily}\n<b>Łącznie przetworzono:</b> {total}\n\n<b>Limity planu:</b>\n• Maks. długość: {max_duration} s\n• Jakość: do {max_quality}\n• Znak wodny: {watermark}\n• Zadań dziennie: {daily}\n\n💎 Użyj /pricing, aby ulepszyć",
        "tr": "👤 <b>Profilin</b>\n\n<b>Plan:</b> {tier} ({status})\n<b>Bugünkü görevler:</b> {today}/{daily}\n<b>Toplam işlenen:</b> {total}\n\n<b>Plan limitleri:</b>\n• Maks. süre: {max_duration} sn\n• Kalite: {max_quality}’e kadar\n• Filigran: {watermark}\n• Günlük görev: {daily}\n\n💎 Yükseltmek için /pricing kullan",
        "uk": "👤 <b>Твій профіль</b>\n\n<b>Тариф:</b> {tier} ({status})\n<b>Задач сьогодні:</b> {today}/{daily}\n<b>Всього оброблено:</b> {total}\n\n<b>Ліміти тарифу:</b>\n• Макс. тривалість: {max_duration} с\n• Якість: до {max_quality}\n• Водяний знак: {watermark}\n• Задач на день: {daily}\n\n💎 Використовуй /pricing для апґрейду",
        "ar": "👤 <b>ملفك الشخصي</b>\n\n<b>الخطة:</b> {tier} ({status})\n<b>مهام اليوم:</b> {today}/{daily}\n<b>الإجمالي المعالج:</b> {total}\n\n<b>حدود الخطة:</b>\n• المدة القصوى: {max_duration} ث\n• الجودة: حتى {max_quality}\n• العلامة المائية: {watermark}\n• المهام اليومية: {daily}\n\n💎 استخدم ‎/pricing‎ للترقية",
        "zh": "👤 <b>你的资料</b>\n\n<b>套餐：</b>{tier}（{status}）\n<b>今日任务：</b>{today}/{daily}\n<b>累计处理：</b>{total}\n\n<b>套餐限制：</b>\n• 最长时长：{max_duration} 秒\n• 画质：最高 {max_quality}\n• 水印：{watermark}\n• 每日任务：{daily}\n\n💎 使用 /pricing 升级",
        "kk": "👤 <b>Профиліңіз</b>\n\n<b>Тариф:</b> {tier} ({status})\n<b>Бүгінгі тапсырмалар:</b> {today}/{daily}\n<b>Барлығы өңделді:</b> {total}\n\n<b>Тариф шектері:</b>\n• Макс. ұзақтық: {max_duration} с\n• Сапа: {max_quality} дейін\n• Сутаңба: {watermark}\n• Күндік тапсырма: {daily}\n\n💎 Жаңарту үшін /pricing пайдаланыңыз",
        "tg": "👤 <b>Профили шумо</b>\n\n<b>Нақша:</b> {tier} ({status})\n<b>Вазифаҳои имрӯз:</b> {today}/{daily}\n<b>Ҳамагӣ коркард шуд:</b> {total}\n\n<b>Маҳдудиятҳои нақша:</b>\n• Давомнокии макс.: {max_duration} с\n• Сифат: то {max_quality}\n• Тамға: {watermark}\n• Вазифаҳо дар рӯз: {daily}\n\n💎 Барои навсозӣ /pricing -ро истифода баред",
        "uz": "👤 <b>Profilingiz</b>\n\n<b>Tarif:</b> {tier} ({status})\n<b>Bugungi vazifalar:</b> {today}/{daily}\n<b>Jami qayta ishlangan:</b> {total}\n\n<b>Tarif cheklovlari:</b>\n• Maks. davomiylik: {max_duration} soniya\n• Sifat: {max_quality} gacha\n• Suv belgisi: {watermark}\n• Kunlik vazifa: {daily}\n\n💎 Yangilash uchun /pricing dan foydalaning",
    },
)

register_key(
    "profile.button",
    {
        "ru": "👤 Профиль",
        "en": "👤 Profile",
        "es": "👤 Perfil",
        "fr": "👤 Profil",
        "de": "👤 Profil",
        "it": "👤 Profilo",
        "pt": "👤 Perfil",
        "pl": "👤 Profil",
        "tr": "👤 Profil",
        "uk": "👤 Профіль",
        "ar": "👤 الملف",
        "zh": "👤 个人资料",
        "kk": "👤 Профиль",
        "tg": "👤 Профил",
        "uz": "👤 Profil",
    },
)








def translate_with_fallback(
    translations: Mapping[str, str],
    language: str,
    *,
    default: str | None = None,
) -> str:
    """Return translation with fallbacks."""
    if language in translations:
        return translations[language]

    for fallback in FALLBACK_LANGUAGES:
        if fallback in translations:
            return translations[fallback]

    if default is not None:
        return default

    raise KeyError(f"Translation missing for {language}")


def t(user_or_lang: Any | None, key: str, **kwargs: Any) -> str:
    """Translate by key for the given user or explicit language."""
    language = resolve_language(user_or_lang)
    translations = TRANSLATIONS_BY_KEY.get(key)
    if translations is None:
        raise KeyError(f"Unknown translation key: {key}")

    text = translate_with_fallback(translations, language)
    if kwargs:
        return text.format(**kwargs)
    return text


def tr(user_or_lang: Any | None, ru_text: str, en_text: str, **kwargs: Any) -> str:
    """Backward-compatible helper: translate based on english text alias."""
    language = resolve_language(user_or_lang)
    translations = TEXT_TRANSLATIONS.get(en_text)
    if translations:
        text = translate_with_fallback(translations, language, default=en_text)
    else:
        text = ru_text if language == "ru" else en_text

    if kwargs:
        return text.format(**kwargs)
    return text


@lru_cache(maxsize=128)
def all_translations_for_key(key: str) -> Iterable[str]:
    """Return all translations for a given key (cached)."""
    translations = TRANSLATIONS_BY_KEY.get(key, {})
    return list(translations.values())


def is_text_for_key(text: str, key: str) -> bool:
    """Return True if text is one of the translations for key."""
    return text in all_translations_for_key(key)


def language_options() -> Dict[str, str]:
    """Return mapping of language code to localized name.

    We intentionally limit this list to the core interface languages that the bot
    fully supports. Extra translations may exist in `SUPPORTED_LANGUAGES`, but we
    do not surface them in the UI.
    """
    preferred_order = ("ru", "en", "es", "fr", "de", "it")
    return {
        code: SUPPORTED_LANGUAGES[code]
        for code in preferred_order
        if code in SUPPORTED_LANGUAGES
    }


