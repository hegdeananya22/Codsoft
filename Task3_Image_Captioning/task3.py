import numpy as np
import os
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, LSTM, Embedding, Concatenate, LayerNormalization
from tensorflow.keras import optimizers

class Config:
    IMAGE_SIZE = (224, 224)
    CNN_OUTPUT_DIM = 1280
    MAX_CAPTION_LENGTH = 40
    VOCAB_SIZE = 10000
    EMBEDDING_DIM = 512
    LSTM_UNITS = 512
    BEAM_SIZE = 3

config = Config()

def prepare_data():
    image_paths = [
        r'C:\Users\91910\Desktop\Codsoft\sample.jpg',
        r'C:\Users\91910\Desktop\Codsoft\sample2.jpg',
        r'C:\Users\91910\Desktop\Codsoft\sample3.jpg'
    ]
    
    captions = [
        ['a cat sitting on a couch', 'a domestic cat resting'],
        ['a dog playing in the park', 'a golden retriever running'],
        ['a beautiful sunset over mountains', 'colorful sky at dusk']
    ]
    
    return dict(zip(image_paths, captions))

class FeatureExtractor:
    def __init__(self):
        base_model = EfficientNetB0(include_top=False, pooling='avg', weights='imagenet')
        self.model = Model(inputs=base_model.input, outputs=base_model.output)
    
    def extract(self, image_path):
        img = load_img(image_path, target_size=config.IMAGE_SIZE)
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = img / 255.0
        return self.model.predict(img, verbose=0).flatten()

class TextProcessor:
    def __init__(self):
        self.tokenizer = Tokenizer(oov_token='<unk>', filters='')
        self.special_tokens = ['<pad>', '<start>', '<end>', '<unk>']
        for token in self.special_tokens:
            self.tokenizer.fit_on_texts([token])
    
    def prepare_text_data(self, image_captions):
        all_captions = []
        for caps in image_captions.values():
            all_captions.extend([f'<start> {cap} <end>' for cap in caps])
        
        self.tokenizer.fit_on_texts(all_captions)
        self.word_to_idx = self.tokenizer.word_index
        self.idx_to_word = {v: k for k, v in self.word_to_idx.items()}
        
        max_len = max(len(cap.split()) for cap in all_captions)
        return min(max_len, config.MAX_CAPTION_LENGTH)

def build_model(text_processor):
    # Image branch
    image_input = Input(shape=(config.CNN_OUTPUT_DIM,))
    image_features = Dense(config.LSTM_UNITS, activation='relu')(image_input)
    image_features = LayerNormalization()(image_features)
    
    # Text branch
    caption_input = Input(shape=(config.MAX_CAPTION_LENGTH,))
    caption_embedding = Embedding(
        input_dim=len(text_processor.word_to_idx) + 1,
        output_dim=config.EMBEDDING_DIM,
        mask_zero=True
    )(caption_input)
    caption_lstm = LSTM(config.LSTM_UNITS, return_sequences=False)(caption_embedding)
    
    # Combined model
    combined = Concatenate()([image_features, caption_lstm])
    dense = Dense(config.LSTM_UNITS * 2, activation='relu')(combined)
    output = Dense(len(text_processor.word_to_idx) + 1, activation='softmax')(dense)
    
    model = Model(inputs=[image_input, caption_input], outputs=output)
    model.compile(loss='categorical_crossentropy', optimizer=optimizers.Adam())
    return model

class CaptionGenerator:
    def __init__(self, model, feature_extractor, text_processor):
        self.model = model
        self.feature_extractor = feature_extractor
        self.text_processor = text_processor
    
    def generate_caption(self, image_path):
        features = self.feature_extractor.extract(image_path)
        features = np.expand_dims(features, axis=0)
        
        # Initialize caption with start token
        start_token = self.text_processor.word_to_idx.get('<start>', 1)
        end_token = self.text_processor.word_to_idx.get('<end>', 2)
        
        caption = [start_token]
        for _ in range(config.MAX_CAPTION_LENGTH):
            seq = pad_sequences([caption], maxlen=config.MAX_CAPTION_LENGTH)
            preds = self.model.predict([features, seq], verbose=0)[0]
            next_word = np.argmax(preds)
            
            if next_word == end_token:
                break
            caption.append(next_word)
        
        # Convert indices to words
        words = []
        for idx in caption:
            word = self.text_processor.idx_to_word.get(idx, '<unk>')
            if word not in ['<start>', '<end>']:
                words.append(word)
        
        return ' '.join(words)

if __name__ == "__main__":
    print("Preparing data...")
    image_captions = prepare_data()
    
    # Verify images exist
    for img_path in image_captions:
        if not os.path.exists(img_path):
            print(f"Error: Image not found - {img_path}")
            exit()
    
    print("Initializing text processor...")
    text_processor = TextProcessor()
    max_length = text_processor.prepare_text_data(image_captions)
    
    print("Building model...")
    model = build_model(text_processor)
    
    print("Initializing caption generator...")
    feature_extractor = FeatureExtractor()
    caption_generator = CaptionGenerator(model, feature_extractor, text_processor)
    
    # Generate captions for all images
    for img_path, true_captions in image_captions.items():
        print(f"\nImage: {os.path.basename(img_path)}")
        print("True captions:")
        for cap in true_captions:
            print(f"- {cap}")
        
        print("\nGenerating caption...")
        try:
            generated = caption_generator.generate_caption(img_path)
            print("Generated caption:", generated)
        except Exception as e:
            print(f"Error generating caption: {str(e)}")