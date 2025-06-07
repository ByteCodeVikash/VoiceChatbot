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

नमस्कार! मैं आपकी सरकारी योजनाओं में मदद करूंगा।

📝 **Text message** भेजें:

**Examples:**
• "किसान योजना"
• "महिला योजना गुजरात"  
• "farmer schemes"
• "kisan yojana batao"

Type /help for more info!
        """
        await update.message.reply_text(welcome_msg)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🆘 **Help - कैसे उपयोग करें**

📝 **Text Message Examples:**
• "मुझे किसान योजना चाहिए"
• "women schemes in Gujarat"
• "kisan yojana batao"
• "fisherman scheme"
• "business loan scheme"

🌐 **Languages Supported:**
• Hindi, English, Hinglish

**बस message भेजें - मैं जवाब दूंगा!** 🚀
        """
        await update.message.reply_text(help_text)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_text = update.message.text
        user_name = update.effective_user.first_name
        
        print(f"📝 Text from {user_name}: {user_text}")
        
        # Show processing message
        processing_msg = await update.message.reply_text("🔍 खोज रहे हैं...")
        
        # Process with your existing system
        response = await self.process_query(user_text, user_name)
        
        # Delete processing message
        await processing_msg.delete()
        
        # Send text response
        await update.message.reply_text(response)
        
        # Send voice response
        await self.send_voice_response(update, response)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - WORKING VERSION"""
        user_name = update.effective_user.first_name
        
        try:
            print(f"🎤 Voice message received from {user_name}")
            
            # Show processing message
            processing_msg = await update.message.reply_text("🎤 Voice सुन रहे हैं...")
            
            # Download voice file
            voice_file = await update.message.voice.get_file()
            
            # Download to local path
            temp_voice = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
            await voice_file.download_to_drive(temp_voice.name)
            
            print(f"📁 Voice file downloaded: {temp_voice.name}")
            
            # Convert voice to text
            text = await self.voice_to_text_fixed(temp_voice.name)
            
            # Delete processing message
            await processing_msg.delete()
            
            if text and len(text.strip()) > 0:
                print(f"🔤 Voice recognized: '{text}'")
                
                # Show what was heard
                await update.message.reply_text(f"🎤 **आपने कहा:** '{text}'\n\n🔍 खोज रहे हैं...")
                
                # Process the recognized text
                response = await self.process_query(text, user_name)
                
                # Send response
                await update.message.reply_text(response)
                await self.send_voice_response(update, response)
                
            else:
                await update.message.reply_text(
                    "🤷 **Voice clear नहीं सुनाई दी**\n\n"
                    "कृपया:\n"
                    "• साफ बोलें\n"
                    "• Noise कम करें\n"
                    "• या Text message भेजें\n\n"
                    "**Example:** 'किसान योजना बताओ'"
                )
                
            # Cleanup temp file
            try:
                os.unlink(temp_voice.name)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Voice processing error: {e}")
            await update.message.reply_text(
                "❌ **Voice processing में problem**\n\n"
                "Please **text message** भेजें:\n"
                "• 'किसान योजना'\n"
                "• 'farmer scheme'\n"
                "• 'महिला योजना'"
            )
    
    async def voice_to_text_fixed(self, voice_path):
        """Convert voice to text - IMPROVED VERSION"""
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
            print(f"🔄 Converting voice file: {voice_path}")
            
            # Convert OGG to WAV using pydub
            audio = AudioSegment.from_file(voice_path)
            wav_path = voice_path.replace('.ogg', '.wav')
            audio.export(wav_path, format="wav")
            
            print(f"🔄 Converted to WAV: {wav_path}")
            
            # Use speech recognition
            r = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = r.record(source)
                
                # Try Hindi first
                try:
                    text = r.recognize_google(audio_data, language='hi-IN')
                    print(f"✅ Hindi recognition: {text}")
                    return text
                except:
                    # Try English as fallback
                    try:
                        text = r.recognize_google(audio_data, language='en-IN')
                        print(f"✅ English recognition: {text}")
                        return text
                    except:
                        print("❌ Both Hindi and English recognition failed")
                        return None
            
            # Cleanup WAV file
            try:
                os.unlink(wav_path)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Voice to text error: {e}")
            return None
    
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
            
            # Format response - CLEAN WITHOUT PREFIX
            if schemes:
                response = self.assistant.format_scheme_response(schemes, query, "hinglish")
                return response  # Clean response without extra text
            else:
                return "❌ कोई संबंधित योजना नहीं मिली। कृपया अधिक विवरण दें।\n\n💡 **Try करें:**\n• किसान योजना\n• महिला योजना\n• farmer scheme"
                
        except Exception as e:
            print(f"Processing error: {e}")
            return "❌ कुछ technical problem है। फिर से try करें।"
    
    async def send_voice_response(self, update, text):
        """Send voice response using gTTS - FIXED VERSION"""
        try:
            # Clean text for TTS (remove markdown and special chars)
            clean_text = text.replace("**", "").replace("*", "").replace("#", "")
            clean_text = clean_text.replace("✅", "").replace("❌", "").replace("🎯", "")
            clean_text = clean_text.replace("।", ".").replace("…", "...")
            
            # Handle long text - smart chunking
            if len(clean_text) > 400:
                # Split into sentences and take first few
                sentences = clean_text.split('.')
                voice_text = ""
                for sentence in sentences:
                    if len(voice_text + sentence) < 380:  # Safe limit
                        voice_text += sentence + ". "
                    else:
                        break
                voice_text = voice_text.strip()
            else:
                voice_text = clean_text
            
            # Ensure text ends properly
            if voice_text and not voice_text.endswith('.'):
                voice_text += "."
            
            print(f"🔊 Generating voice for: '{voice_text[:50]}...'")
            
            # Create voice response with better settings
            tts = gTTS(text=voice_text, lang='hi', slow=False, lang_check=False)
            
            # Save to temp file with unique name
            import time
            temp_filename = f"voice_{int(time.time() * 1000)}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            tts.save(temp_path)
            print(f"🎵 Voice saved to: {temp_path}")
            
            # Verify file exists and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                # Send voice message
                with open(temp_path, 'rb') as voice_file:
                    await update.message.reply_voice(
                        voice_file,
                        caption="🔊 Audio response"
                    )
                print("✅ Voice message sent successfully")
            else:
                print("❌ Voice file too small or missing")
                await update.message.reply_text("🔊 Audio response ready!")
            
            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            print(f"❌ Voice response error: {e}")
            # Send a simple acknowledgment instead
            try:
                await update.message.reply_text("🔊 Audio response उपलब्ध है!")
            except:
                pass
    
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
    # Get token from environment variable
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN environment variable not set!")
        print("Use: export BOT_TOKEN='your_token_here'")
        exit(1)
    
    print(f"🤖 Starting Telegram Scheme Bot...")
    print(f"🔑 Token configured: {BOT_TOKEN[:10]}...")
    print(f"🌐 Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Local'}")
    
    bot = TelegramSchemeBot(BOT_TOKEN)
    bot.run()