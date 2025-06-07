import os
import asyncio
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import subprocess

from voice_assistant import EnhancedVoiceAssistant
from config import CONFIG

class TelegramSchemeBot:
    def __init__(self, token):
        self.token = token
        # Tumhara existing assistant use karo
        self.assistant = EnhancedVoiceAssistant()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_msg = """
🤖 **Government Schemes Assistant**

मैं आपकी सरकारी योजनाओं में मदद करूंगा!

📝 **Text message** भेजें या 🎤 **Voice message** भेजें

Examples:
- "किसान योजना"
- "महिला योजना"  
- "farmer schemes"

Type /help for more info!
        """
        await update.message.reply_text(welcome_msg)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🆘 **Help - कैसे उपयोग करें**

1️⃣ **Text Message**: "farmer scheme batao"
2️⃣ **Voice Message**: Record करके भेजें
3️⃣ **Languages**: Hindi, English, Hinglish

**Examples:**
- "मुझे किसान योजना चाहिए"
- "women schemes in Gujarat"
- "kisan yojana batao"

बस message भेजें - मैं जवाब दूंगा! 🚀
        """
        await update.message.reply_text(help_text)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_text = update.message.text
        user_name = update.effective_user.first_name
        
        print(f"📝 Text from {user_name}: {user_text}")
        
        # Process with your existing system
        response = await self.process_query(user_text, user_name)
        
        # Send text response
        await update.message.reply_text(response)
        
        # Send voice response
        await self.send_voice_response(update, response)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        user_name = update.effective_user.first_name
        
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_path = await voice_file.download_to_drive()
            
            print(f"🎤 Voice from {user_name}: Processing...")
            
            # Convert voice to text (basic implementation)
            text = await self.voice_to_text(voice_path)
            
            if text:
                print(f"🔤 Recognized: {text}")
                response = await self.process_query(text, user_name)
                
                await update.message.reply_text(f"🎤 मैंने सुना: '{text}'\n\n{response}")
                await self.send_voice_response(update, response)
            else:
                await update.message.reply_text("🤷 Voice समझ नहीं आया। Text message भेजें।")
                
        except Exception as e:
            print(f"Voice error: {e}")
            await update.message.reply_text("❌ Voice processing failed. Text भेजें।")
    
    async def process_query(self, query, user_name):
        """Process query using your existing system"""
        try:
            # Set user context
            self.assistant.user_name = user_name
            self.assistant.user_context["name"] = user_name
            
            # Parse occupation/location (simplified)
            occupation, location = self.assistant.parse_user_occupation(query)
            if occupation:
                self.assistant.user_context["occupation"] = occupation
            if location:
                self.assistant.user_context["location"] = location
            
            # Find schemes using your RAG system
            schemes = self.assistant.find_relevant_schemes(query, top_n=3)
            
            # Format response
            if schemes:
                response = self.assistant.format_scheme_response(schemes, query, "hinglish")
                return f"✅ **मिली योजनाएं:**\n\n{response}"
            else:
                return "❌ कोई योजना नहीं मिली। अधिक details दें।"
                
        except Exception as e:
            print(f"Processing error: {e}")
            return "❌ कुछ गलत हुआ। फिर से try करें।"
    
    async def voice_to_text(self, voice_path):
        """Convert voice to text (simplified)"""
        try:
            # Basic implementation - you can improve this
            # Using speech_recognition library
            import speech_recognition as sr
            
            r = sr.Recognizer()
            with sr.AudioFile(voice_path) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language='hi-IN')
                return text
        except:
            return None
    
    async def send_voice_response(self, update, text):
        """Send voice response using gTTS"""
        try:
            # Create voice response
            tts = gTTS(text=text[:200], lang='hi', slow=False)  # Limit length
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            
            # Send voice message
            with open(temp_file.name, 'rb') as voice:
                await update.message.reply_voice(voice)
            
            # Cleanup
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"Voice response error: {e}")
    
    def run(self):
        """Run the bot"""
        app = Application.builder().token(self.token).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        
        print("🤖 Telegram Bot starting...")
        app.run_polling()

if __name__ == "__main__":
    # Your bot token here
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    bot = TelegramSchemeBot(BOT_TOKEN)
    bot.run()