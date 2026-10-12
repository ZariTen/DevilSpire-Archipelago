// ap_chest_init(): obj_chest Create (called in the chest's context instead of the vanilla loot roll) for the Archipelago chest.
ap_chest = 1;
locked = 0;
texF = background_get_texture(tex_chestF3);
texS = background_get_texture(tex_chestS3);
texT = background_get_texture(tex_chestT3);
texL = background_get_texture(tex_chestL2);
texH = background_get_texture(tex_chestH2);
item = generate_gold(1); // placeholder visual only; its content is never picked up (interact -> ap_chest_open)
open = 0;
kicked = 0;
float = 0;
spin = 0;
z = 0;
z2 = 8;
sound_emitter = audio_emitter_create();
audio_emitter_position(sound_emitter, x, y, 0);
image_speed = 0;
drawdelay = irandom(60);
